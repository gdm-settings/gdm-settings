import os
import logging
from gettext import gettext as _, pgettext as C_
from gi.repository import GObject, Gio
from .info import application_id
from . import env
from . import gr_utils

def delayed_settings(schema_id):
    settings = Gio.Settings.new(schema_id)
    settings.delay()
    return settings

main_settings         = delayed_settings(application_id)
appearance_settings   = delayed_settings(f'{application_id}.appearance')
font_settings         = delayed_settings(f'{application_id}.fonts')
login_screen_settings = delayed_settings(f'{application_id}.misc')
night_light_settings  = delayed_settings(f'{application_id}.night-light')
mouse_settings        = delayed_settings(f'{application_id}.mouse')
power_settings        = delayed_settings(f'{application_id}.power')
touchpad_settings     = delayed_settings(f'{application_id}.touchpad')
sound_settings        = delayed_settings(f'{application_id}.sound')
top_bar_settings      = delayed_settings(f'{application_id}.top-bar')

all_settings = (
    main_settings,
    appearance_settings,
    font_settings,
    login_screen_settings,
    night_light_settings,
    mouse_settings,
    power_settings,
    touchpad_settings,
    sound_settings,
    top_bar_settings,
)

class LogoImageNotFoundError (FileNotFoundError): pass

def _Settings(schema_id):
    if schema := Gio.SettingsSchemaSource.get_default().lookup(schema_id, recursive=True):
        return Gio.Settings(schema_id=schema_id)

class SettingsManager (GObject.Object):

    def __init__(self):
        super().__init__()

        from .utils import CommandElevator
        self.command_elevator = CommandElevator()

        from .enums import PackageType
        if main_settings["never-applied"] and env.PACKAGE_TYPE is not PackageType.Flatpak:
            self.load_session_settings()

    def load_session_settings(self):
        '''Load user's Gnome settings into the app'''


        if user_settings := _Settings('org.gnome.shell.extensions.user-theme'):
            appearance_settings['shell-theme'] = user_settings['name'] or 'default'

        if user_settings := _Settings("org.gnome.desktop.interface"):
            appearance_settings['icon-theme'] = user_settings["icon-theme"]
            appearance_settings['cursor-theme'] = user_settings["cursor-theme"]

            font_settings['font'] = user_settings["font-name"]
            font_settings['antialiasing'] = user_settings["font-antialiasing"]
            font_settings['hinting'] = user_settings["font-hinting"]
            font_settings['scaling-factor'] = user_settings["text-scaling-factor"]

            top_bar_settings['show-weekday'] = user_settings["clock-show-weekday"]
            top_bar_settings['time-format'] = user_settings["clock-format"]
            top_bar_settings['show-seconds'] = user_settings["clock-show-seconds"]
            top_bar_settings['show-battery-percentage'] = user_settings["show-battery-percentage"]

        if user_settings := _Settings("org.gnome.desktop.sound"):
            sound_settings['theme'] = user_settings["theme-name"]
            sound_settings['event-sounds'] = user_settings["event-sounds"]
            sound_settings['feedback-sounds'] = user_settings["input-feedback-sounds"]
            sound_settings['over-amplification'] = user_settings["allow-volume-above-100-percent"]

        if user_settings := _Settings("org.gnome.desktop.peripherals.mouse"):
            mouse_settings['pointer-acceleration'] = user_settings["accel-profile"]
            mouse_settings['natural-scrolling'] = user_settings["natural-scroll"]
            mouse_settings['speed'] = user_settings["speed"]

        if user_settings := _Settings("org.gnome.desktop.peripherals.touchpad"):
            touchpad_settings['tap-to-click'] = user_settings["tap-to-click"]
            touchpad_settings['natural-scrolling'] = user_settings["natural-scroll"]
            touchpad_settings['two-finger-scrolling'] = user_settings["two-finger-scrolling-enabled"]
            touchpad_settings['disable-while-typing'] = user_settings["disable-while-typing"]
            touchpad_settings['speed'] = user_settings["speed"]

        if user_settings := _Settings("org.gnome.settings-daemon.plugins.power"):
            power_settings['power-button-action'] = user_settings['power-button-action']
            power_settings['auto-power-saver'] = user_settings['power-saver-profile-on-low-battery']
            power_settings['dim-screen'] = user_settings['idle-dim']
            power_settings['suspend-on-ac'] = user_settings['sleep-inactive-ac-type'] == 'suspend'
            power_settings['suspend-on-ac-delay'] = user_settings['sleep-inactive-ac-timeout'] / 60
            power_settings['suspend-on-battery'] = user_settings['sleep-inactive-battery-type'] == 'suspend'
            power_settings['suspend-on-battery-delay'] = user_settings['sleep-inactive-battery-timeout'] / 60

        if user_settings := _Settings("org.gnome.desktop.session"):
            if user_settings['idle-delay']:
                power_settings['blank-screen'] = True
                power_settings['idle-delay'] = user_settings['idle-delay'] / 60
            else:
                power_settings['blank-screen'] = False

        if user_settings := _Settings("org.gnome.settings-daemon.plugins.color"):
            night_light_settings['enabled'] = user_settings["night-light-enabled"]
            night_light_settings['schedule-automatic'] = user_settings["night-light-schedule-automatic"]
            night_light_settings['temperature'] = user_settings["night-light-temperature"]

            from math import trunc
            def hour_minute(decimal_time):
                hour = trunc(decimal_time)
                minute = round((decimal_time % 1) * 60)
                if minute == 60:
                    hour += 1
                    minute = 0
                return hour, minute

            start_time = user_settings["night-light-schedule-from"]
            start_hour, start_minute = hour_minute(start_time)
            night_light_settings['start-hour'] = start_hour
            night_light_settings['start-minute'] = start_minute

            end_time = user_settings["night-light-schedule-to"]
            end_hour, end_minute = hour_minute(end_time)
            night_light_settings['end-hour'] = end_hour
            night_light_settings['end-minute'] = end_minute

        if user_settings := _Settings("org.gnome.login-screen"):
            login_screen_settings['enable-welcome-message'] = user_settings["banner-message-enable"]
            login_screen_settings['welcome-message'] = user_settings["banner-message-text"]
            login_screen_settings['logo'] = user_settings["logo"]
            login_screen_settings['enable-logo'] = bool(user_settings["logo"])
            login_screen_settings['disable-restart-buttons'] = user_settings["disable-restart-buttons"]
            login_screen_settings['disable-user-list'] = user_settings["disable-user-list"]

    def save_settings(self):
        '''Save settings to GSettings of this app'''
        for settings in all_settings:
            settings.apply()

    def drop_changes(self):
        '''Save settings to GSettings of this app'''
        for settings in all_settings:
            settings.revert()

    def get_setting_css(self) -> str:
        '''Get CSS for current settings (to append to theme's 'gnome-shell.css' resource)'''

        css = "\n\n/* 'Login Manager Settings' App Provided CSS */\n"

        ### Background ###
        from .enums import BackgroundType
        background_type = BackgroundType[appearance_settings['background-type']]
        background_image = appearance_settings['background-image']
        if background_type is BackgroundType.image and background_image:
            css += "#lockDialogGroup {\n"
            css += "  background-image: url('resource:///org/gnome/shell/theme/background');\n"
            css += "  background-size: cover;\n"
            css += "}\n"
        elif background_type is BackgroundType.color:
            background_color = appearance_settings['background-color']
            css += "#lockDialogGroup { background-color: "+ background_color + "; }\n"

        ### Top Bar ###
        def select_elem(elem:str='') -> str:
            if elem:
                return f"#panel .{elem}, #panel.login-screen .{elem}, #panel.unlock-screen .{elem}"
            else:
                return f"#panel, #panel.login-screen, #panel.unlock-screen"

        disable_arrows = top_bar_settings['disable-arrows']
        disable_rounded_corners = top_bar_settings['disable-rounded-corners']
        change_text_color = top_bar_settings['change-text-color']
        text_color = top_bar_settings['text-color']
        change_background_color = top_bar_settings['change-background-color']
        background_color = top_bar_settings['background-color']

        # Arrows
        if disable_arrows:
            css += select_elem("popup-menu-arrow") + " { width: 0px; }\n"
        # Rounded Corners
        if disable_rounded_corners:
            css +=  select_elem("panel-corner")
            css +=  " {\n"
            css += f"  -panel-corner-opacity: 0;\n"
            css +=  "}\n"
        # Text Color
        if change_text_color:
            css +=  select_elem('panel-button')
            css +=  " {\n"
            css += f"  color: {text_color};\n"
            css +=  "}\n"
        # Background Color
        if change_background_color:
            css +=  select_elem()
            css +=  " {\n"
            css += f"  background-color: {background_color};\n"
            css +=  "}\n"
            if not disable_rounded_corners:
                css +=  select_elem("panel-corner")
                css +=  " {\n"
                css += f"  -panel-corner-opacity: 1;\n"
                css += f"  -panel-corner-background-color: {background_color};\n"
                css +=  "}\n"

        # Large Welcome Message
        if login_screen_settings['enlarge-welcome-message']:
            css += ".login-dialog-banner {\n"
            css += "  font-size: 1.5em;\n"
            css += "  font-weight: bold;\n"
            css += "}\n"

        return css

    def backup_default_shell_theme (self):
        '''back up the default shell theme (if needed)'''

        logging.info(_("Backing up default shell theme …"))

        if gr_utils.is_unmodified(gr_utils.ShellGresourceFile):
            self.command_elevator.add(f"cp {gr_utils.ShellGresourceFile} {gr_utils.ShellGresourceAutoBackup}")

        from os import makedirs
        makedirs(env.TEMP_DIR, exist_ok=True)

        gr_utils.extract_default_theme(f'{env.TEMP_DIR}/default-pure')

        self.command_elevator.add(f"rm -rf {gr_utils.ThemesDir}/default-pure")
        self.command_elevator.add(f"mkdir -p {gr_utils.ThemesDir}")
        self.command_elevator.add(f"cp -r {env.TEMP_DIR}/default-pure -t {gr_utils.ThemesDir}")

    def apply_shell_theme_settings(self):
        ''' Apply settings that require modification of 'gnome-shell-theme.gresource' file '''

        from .enums import BackgroundType
        from .theme_lists import shell_themes

        # If needed, back up the default shell theme

        pure_theme_not_exists = 'default-pure' not in shell_themes.names
        shell_gresource_is_stock = gr_utils.is_unmodified(gr_utils.ShellGresourceFile)

        if shell_gresource_is_stock or pure_theme_not_exists:
            self.backup_default_shell_theme()


        # Apply shell theme settings

        theme_name = appearance_settings['shell-theme']
        theme_path = shell_themes.get_path(theme_name)
        shelldir   = os.path.join(theme_path, 'gnome-shell') if theme_path else None

        background_type = BackgroundType[appearance_settings['background-type']]
        background_image = None
        if background_type is BackgroundType.image:
            background_image = appearance_settings['background-image']

        compiled_file = gr_utils.compile(shelldir,
              additional_css=self.get_setting_css(),
            background_image=background_image
        )

        # We need to copy the compiled gresource file instead of moving it because the copy gets correct
        # SELinux context/label where applicable and prevents breakage of GDM in such situations.
        if gr_utils.UbuntuGdmGresourceFile:
            logging.info(C_('Command-line output', "Applying GResource settings for Ubuntu …"))
            self.command_elevator.add(f"cp {compiled_file} {gr_utils.CustomGresourceFile}")
            self.command_elevator.add(f"chown root: {gr_utils.CustomGresourceFile}")
            self.command_elevator.add(f"chmod 644 {gr_utils.CustomGresourceFile}")
            self.command_elevator.add(f'update-alternatives --quiet --install {gr_utils.UbuntuGdmGresourceFile} {os.path.basename(gr_utils.UbuntuGdmGresourceFile)} {gr_utils.CustomGresourceFile} 0')
            self.command_elevator.add(f'update-alternatives --quiet --set {os.path.basename(gr_utils.UbuntuGdmGresourceFile)} {gr_utils.CustomGresourceFile}')
        else:
            logging.info(C_('Command-line output', "Applying GResource settings for non-Ubuntu systems …"))
            self.command_elevator.add(f"cp {compiled_file} {gr_utils.ShellGresourceFile}")
            self.command_elevator.add(f"chown root: {gr_utils.ShellGresourceFile}")
            self.command_elevator.add(f"chmod 644 {gr_utils.ShellGresourceFile}")

    def apply_dconf_settings(self):
        ''' Apply settings that are applied through 'dconf' '''

        gdm_conf_dir = "/etc/dconf/db/gdm.d"
        gdm_profile_dir = "/etc/dconf/profile"
        gdm_profile_path = f"{gdm_profile_dir}/gdm"

        temp_profile_path = f"{env.TEMP_DIR}/gdm-profile"
        with open(temp_profile_path, "w+") as temp_profile_file:
            gdm_profile_contents  = "user-db:user\n"
            gdm_profile_contents += "system-db:gdm\n"
            gdm_profile_contents += "file-db:/usr/share/gdm/greeter-dconf-defaults\n"
            temp_profile_file.write(gdm_profile_contents)

        temp_conf_path = f"{env.TEMP_DIR}/95-gdm-settings"
        with open(temp_conf_path, "w+") as temp_conf_file:

            font = font_settings['font']
            hinting = font_settings['hinting']
            icon_theme = appearance_settings['icon-theme']
            time_format = top_bar_settings['time-format']
            cursor_theme = appearance_settings['cursor-theme']
            show_seconds = str(top_bar_settings['show-seconds']).lower()
            show_weekday = str(top_bar_settings['show-weekday']).lower()
            antialiasing = font_settings['antialiasing']
            scaling_factor = font_settings['scaling-factor']
            show_battery_percentage = str(top_bar_settings['show-battery-percentage']).lower()

            gdm_conf_contents  =  "#-------- Interface ---------\n"
            gdm_conf_contents +=  "[org/gnome/desktop/interface]\n"
            gdm_conf_contents +=  "#----------------------------\n"
            gdm_conf_contents += f"cursor-theme='{cursor_theme}'\n"
            gdm_conf_contents += f"icon-theme='{icon_theme}'\n"
            gdm_conf_contents += f"show-battery-percentage={show_battery_percentage}\n"
            gdm_conf_contents += f"clock-show-seconds={show_seconds}\n"
            gdm_conf_contents += f"clock-show-weekday={show_weekday}\n"
            gdm_conf_contents += f"clock-format='{time_format}'\n"
            gdm_conf_contents += f"font-name='{font}'\n"
            gdm_conf_contents += f"font-antialiasing='{antialiasing}'\n"
            gdm_conf_contents += f"font-hinting='{hinting}'\n"
            gdm_conf_contents += f"text-scaling-factor={scaling_factor}\n"
            gdm_conf_contents +=  "\n"

            sound_theme = sound_settings['theme']
            event_sounds = str(sound_settings['event-sounds']).lower()
            feedback_sounds = str(sound_settings['feedback-sounds']).lower()
            over_amplification = str(sound_settings['over-amplification']).lower()

            gdm_conf_contents +=  "#-------- Sound ---------\n"
            gdm_conf_contents +=  "[org/gnome/desktop/sound]\n"
            gdm_conf_contents +=  "#------------------------\n"
            gdm_conf_contents += f"theme-name='{sound_theme}'\n"
            gdm_conf_contents += f"event-sounds={event_sounds}\n"
            gdm_conf_contents += f"input-feedback-sounds={feedback_sounds}\n"
            gdm_conf_contents += f"allow-volume-above-100-percent={over_amplification}\n"
            gdm_conf_contents +=  "\n"

            pointer_acceleration = mouse_settings['pointer-acceleration']
            natural_scrolling = str(mouse_settings['natural-scrolling']).lower()
            mouse_speed = mouse_settings['speed']

            gdm_conf_contents +=  "#-------------- Mouse ---------------\n"
            gdm_conf_contents +=  "[org/gnome/desktop/peripherals/mouse]\n"
            gdm_conf_contents +=  "#------------------------------------\n"
            gdm_conf_contents += f"accel-profile='{pointer_acceleration}'\n"
            gdm_conf_contents += f"natural-scroll={natural_scrolling}\n"
            gdm_conf_contents += f"speed={mouse_speed}\n"
            gdm_conf_contents +=  "\n"

            touchpad_speed = touchpad_settings['speed']
            tap_to_click = str(touchpad_settings['tap-to-click']).lower()
            natural_scrolling = str(touchpad_settings['natural-scrolling']).lower()
            two_finger_scrolling = str(touchpad_settings['two-finger-scrolling']).lower()
            disable_while_typing = str(touchpad_settings['disable-while-typing']).lower()

            gdm_conf_contents +=  "#-------------- Touchpad ---------------\n"
            gdm_conf_contents +=  "[org/gnome/desktop/peripherals/touchpad]\n"
            gdm_conf_contents +=  "#---------------------------------------\n"
            gdm_conf_contents += f"speed={touchpad_speed}\n"
            gdm_conf_contents += f"tap-to-click={tap_to_click}\n"
            gdm_conf_contents += f"natural-scroll={natural_scrolling}\n"
            gdm_conf_contents += f"two-finger-scrolling-enabled={two_finger_scrolling}\n"
            gdm_conf_contents += f"disable-while-typing={disable_while_typing}\n"
            gdm_conf_contents +=  "\n"

            power_button_action = power_settings['power-button-action']
            auto_power_saver = str(power_settings['auto-power-saver']).lower()
            dim_screen = str(power_settings['dim-screen']).lower()
            idle_delay = int(power_settings['idle-delay'] * 60) if power_settings['blank-screen'] else 0
            sleep_type_on_ac = 'suspend' if power_settings['suspend-on-ac'] else 'nothing'
            suspend_on_ac_delay = int(power_settings['suspend-on-ac-delay'] * 60)
            sleep_type_on_battery = 'suspend' if power_settings['suspend-on-battery'] else 'nothing'
            suspend_on_battery_delay = int(power_settings['suspend-on-battery-delay'] * 60)

            gdm_conf_contents +=  "#---------------- Power -----------------\n"
            gdm_conf_contents +=  "[org/gnome/settings-daemon/plugins/power]\n"
            gdm_conf_contents +=  "#----------------------------------------\n"
            gdm_conf_contents += f"power-button-action='{power_button_action}'\n"
            gdm_conf_contents += f"power-saver-profile-on-low-battery={auto_power_saver}\n"
            gdm_conf_contents += f"dim-screen={dim_screen}\n"
            gdm_conf_contents += f"sleep-inactive-ac-type='{sleep_type_on_ac}'\n"
            gdm_conf_contents += f"sleep-inactive-ac-timeout={suspend_on_ac_delay}\n"
            gdm_conf_contents += f"sleep-inactive-battery-type='{sleep_type_on_battery}'\n"
            gdm_conf_contents += f"sleep-inactive-battery-timeout={suspend_on_battery_delay}\n"
            gdm_conf_contents +=  "\n"
            gdm_conf_contents +=  "#--------------- Session ----------------\n"
            gdm_conf_contents +=  "[org/gnome/desktop/session]\n"
            gdm_conf_contents +=  "#----------------------------------------\n"
            gdm_conf_contents += f"idle-delay={idle_delay}\n"
            gdm_conf_contents +=  "\n"

            enabled = str(night_light_settings['enabled']).lower()
            temperature = round(night_light_settings['temperature'])
            schedule_automatic = str(night_light_settings['schedule-automatic']).lower()
            schedule_from  = night_light_settings['start-hour']
            schedule_from += night_light_settings['start-minute'] / 60
            schedule_to  = night_light_settings['end-hour']
            schedule_to += night_light_settings['end-minute'] / 60 

            gdm_conf_contents +=  "#------------- Night Light --------------\n"
            gdm_conf_contents +=  "[org/gnome/settings-daemon/plugins/color]\n"
            gdm_conf_contents +=  "#----------------------------------------\n"
            gdm_conf_contents += f"night-light-enabled={enabled}\n"
            gdm_conf_contents += f"night-light-temperature=uint32 {temperature}\n"
            gdm_conf_contents += f"night-light-schedule-automatic={schedule_automatic}\n"
            gdm_conf_contents += f"night-light-schedule-from={schedule_from}\n"
            gdm_conf_contents += f"night-light-schedule-to={schedule_to}\n"
            gdm_conf_contents +=  "\n"

            enable_logo = login_screen_settings['enable-logo']
            logo = '/etc/gdm-logo' if enable_logo else ''
            logo_file = login_screen_settings['logo'].removeprefix(env.HOST_ROOT)
            enable_welcome_message = str(login_screen_settings['enable-welcome-message']).lower()
            welcome_message = login_screen_settings['welcome-message'].replace("'", r"\'")
            disable_restart_buttons = str(login_screen_settings['disable-restart-buttons']).lower()
            disable_user_list = str(login_screen_settings['disable-user-list']).lower()

            gdm_conf_contents +=  "#----- Login Screen ----\n"
            gdm_conf_contents +=  "[org/gnome/login-screen]\n"
            gdm_conf_contents +=  "#-----------------------\n"
            gdm_conf_contents += f"logo='{logo}'\n"
            gdm_conf_contents += f"banner-message-enable={enable_welcome_message}\n"
            gdm_conf_contents += f"banner-message-text='{welcome_message}'\n"
            gdm_conf_contents += f"disable-restart-buttons={disable_restart_buttons}\n"
            gdm_conf_contents += f"disable-user-list={disable_user_list}\n"

            temp_conf_file.write(gdm_conf_contents)

        if enable_logo and logo_file:
            if not os.path.exists(logo_file):
                raise LogoImageNotFoundError(2, 'No such file', logo_file)

            from shutil import copy
            logo_temp = os.path.join(env.TEMP_DIR, 'logo.temp')
            copy(logo_file, logo_temp)
            self.command_elevator.add(f"cp -fT '{logo_temp}' '{logo}'")

        overriding_files = self.get_overriding_files()
        if overriding_files:
            self.command_elevator.add(['rm', *overriding_files])

        self.command_elevator.add(f"mkdir -p '{gdm_conf_dir}' '{gdm_profile_dir}'")
        self.command_elevator.add(f"cp -f '{temp_conf_path}' -t '{gdm_conf_dir}'")
        self.command_elevator.add(f"cp -fT '{temp_profile_path}' '{gdm_profile_path}'")
        self.command_elevator.add("dconf update")

    def apply_settings(self) -> bool:
        ''' Apply all settings '''

        self.apply_shell_theme_settings()
        self.apply_dconf_settings()

        status = self.command_elevator.run()

        if status.success:
            # When we change GDM shell theme it becomes the 'default' theme but for the users
            # who didn't want to change shell theme for their session, we need to set it to a
            # pure/original version of the default shell theme
            # Note: We don't want to change user's shell theme if user set it explicitly to
            # 'default' in order to match their GDM theme
            if user_settings := _Settings('org.gnome.shell.extensions.user-theme'):
                if (user_settings['name'] == ''
                and main_settings["never-applied"]):
                    user_settings['name'] = 'default-pure'

            main_settings["never-applied"] = False
            self.save_settings()

        return status

    def apply_user_display_settings(self) -> bool:
        ''' Apply user's current display settings '''

        user_monitors_xml = os.path.join(env.XDG_CONFIG_HOME, 'monitors.xml')

        if not os.path.isfile(user_monitors_xml):
            raise FileNotFoundError(2, 'No such file or directory', user_monitors_xml)

        self.command_elevator.add(['machinectl', 'shell', '{gr_utils.GdmUsername}@', '/usr/bin/env',
                                   'gsettings', 'set', 'experimental-features',
                                   '"[\'scale-monitor-framebuffer\']"',
                                   '&>/dev/null',
                                 ])

        self.command_elevator.add(['install', '-Dm644',
                                   user_monitors_xml,
                                   f'~{gr_utils.GdmUsername}/.config/monitors.xml',
                                 ])

        self.command_elevator.add(['chown', f'{gr_utils.GdmUsername}:',
                                   f'~{gr_utils.GdmUsername}/.config/monitors.xml',
                                 ])

        return self.command_elevator.run()

    def reset_settings(self) -> bool:
        if gr_utils.UbuntuGdmGresourceFile:
            logging.info(C_('Command-line output', "Resetting GResource settings for Ubuntu …"))
            self.command_elevator.add(['update-alternatives',  '--quiet',  '--remove',
                                        os.path.basename(gr_utils.UbuntuGdmGresourceFile),
                                        gr_utils.CustomGresourceFile,
                                     ])
            self.command_elevator.add(f'rm -f {gr_utils.CustomGresourceFile}')
        elif os.path.exists(gr_utils.ShellGresourceAutoBackup):
            logging.info(C_('Command-line output', "Resetting GResource settings for non-Ubuntu systems …"))
            self.command_elevator.add(['mv', '-f',
                                       gr_utils.ShellGresourceAutoBackup,
                                       gr_utils.ShellGresourceFile,
                                     ])
            self.command_elevator.add(f"chown root: {gr_utils.ShellGresourceFile}")
            self.command_elevator.add(f"chmod 644 {gr_utils.ShellGresourceFile}")

        self.command_elevator.add("rm -f /etc/dconf/profile/gdm")
        self.command_elevator.add("rm -f /etc/dconf/db/gdm.d/95-gdm-settings")
        self.command_elevator.add("dconf update")

        if self.command_elevator.run():

            for settings in all_settings:
                for key in settings.props.settings_schema.list_keys():
                    settings.reset(key)
                settings.apply()

            return True

        return False

    def get_overriding_files(self):
        gdm_conf_dir = "/etc/dconf/db/gdm.d"
        our_config = os.path.join(gdm_conf_dir, '95-gdm-settings')
        overriding_files = []

        if os.path.isdir (env.HOST_ROOT + gdm_conf_dir):
            files = set()
            for dirpath, dirnames, filenames in os.walk(env.HOST_ROOT + gdm_conf_dir):
                for filename in filenames:
                    files.add(os.path.join(dirpath.removeprefix(env.HOST_ROOT), filename))
            files.add(our_config)

            sorted_files = sorted (files)
            index_of_next_file = sorted_files.index(our_config) + 1
            overriding_files = sorted_files[index_of_next_file:]

        return overriding_files

    def cleanup(self):
        from shutil import rmtree
        rmtree(path=env.TEMP_DIR, ignore_errors=True)
