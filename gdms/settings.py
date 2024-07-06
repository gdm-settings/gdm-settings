import os
import shutil
import logging
import sys
from math import trunc
from configparser import ConfigParser, ParsingError
from gettext import gettext as _, pgettext as C_

from gi.repository import Gio

from gdms import APP_ID
from gdms import env
from gdms import gresource
from gdms.cmd import CommandList
from gdms.enums import PackageType, BackgroundType
from gdms.utils import GSettings
from gdms.themes import shell_themes

logger = logging.getLogger(__name__)


main_settings          = GSettings.new_delayed(APP_ID)
accessibility_settings = GSettings.new_delayed(APP_ID + '.accessibility')
appearance_settings    = GSettings.new_delayed(APP_ID + '.appearance')
font_settings          = GSettings.new_delayed(APP_ID + '.fonts')
login_screen_settings  = GSettings.new_delayed(APP_ID + '.misc')
night_light_settings   = GSettings.new_delayed(APP_ID + '.night-light')
mouse_settings         = GSettings.new_delayed(APP_ID + '.mouse')
pointing_settings      = GSettings.new_delayed(APP_ID + '.pointing')
power_settings         = GSettings.new_delayed(APP_ID + '.power')
touchpad_settings      = GSettings.new_delayed(APP_ID + '.touchpad')
sound_settings         = GSettings.new_delayed(APP_ID + '.sound')
top_bar_settings       = GSettings.new_delayed(APP_ID + '.top-bar')


all_settings = (
    main_settings,
    accessibility_settings,
    appearance_settings,
    font_settings,
    login_screen_settings,
    night_light_settings,
    mouse_settings,
    pointing_settings,
    power_settings,
    touchpad_settings,
    sound_settings,
    top_bar_settings,
)


class LogoImageNotFoundError (FileNotFoundError): pass


def _GSettings(schema_id):
    if Gio.SettingsSchemaSource.get_default().lookup(schema_id, recursive=True):
        return GSettings(schema_id)


_commands = CommandList()


def init():
    '''Initialize the settings module'''
    os.makedirs(env.TEMP_DIR, exist_ok=True)
    if main_settings["never-applied"] and env.PACKAGE_TYPE is not PackageType.Flatpak:
        load_from_session()


def finalize():
    '''Finalize the settings module'''
    shutil.rmtree(path=env.TEMP_DIR, ignore_errors=True)


def load_from_session():
    '''Load user's Gnome settings into the app'''

    if user_settings := _GSettings('org.gnome.shell.extensions.user-theme'):
        appearance_settings['shell-theme'] = user_settings['name']

    if user_settings := _GSettings("org.gnome.desktop.a11y"):
        source_key = "always-show-universal-access-status"
        target_key = "always-show-accessibility-menu"
        accessibility_settings[target_key] = user_settings[source_key]

    if user_settings := _GSettings("org.gnome.desktop.interface"):
        appearance_settings['icon-theme'] = user_settings["icon-theme"]
        appearance_settings['cursor-theme'] = user_settings["cursor-theme"]

        font_settings['font'] = user_settings["font-name"]
        font_settings['antialiasing'] = user_settings["font-antialiasing"]
        font_settings['hinting'] = user_settings["font-hinting"]
        font_settings['scaling-factor'] = user_settings["text-scaling-factor"]

        pointing_settings['cursor-size'] = user_settings["cursor-size"]

        top_bar_settings['show-weekday'] = user_settings["clock-show-weekday"]
        top_bar_settings['time-format'] = user_settings["clock-format"]
        top_bar_settings['show-seconds'] = user_settings["clock-show-seconds"]
        top_bar_settings['show-battery-percentage'] = user_settings["show-battery-percentage"]

    if user_settings := _GSettings("org.gnome.desktop.sound"):
        sound_settings['theme'] = user_settings["theme-name"]
        sound_settings['event-sounds'] = user_settings["event-sounds"]
        sound_settings['feedback-sounds'] = user_settings["input-feedback-sounds"]
        sound_settings['over-amplification'] = user_settings["allow-volume-above-100-percent"]

    if user_settings := _GSettings("org.gnome.desktop.peripherals.mouse"):
        mouse_settings['pointer-acceleration'] = user_settings["accel-profile"]
        mouse_settings['natural-scrolling'] = user_settings["natural-scroll"]
        mouse_settings['speed'] = user_settings["speed"]

    if user_settings := _GSettings("org.gnome.desktop.peripherals.touchpad"):
        touchpad_settings['tap-to-click'] = user_settings["tap-to-click"]
        touchpad_settings['natural-scrolling'] = user_settings["natural-scroll"]
        touchpad_settings['two-finger-scrolling'] = user_settings["two-finger-scrolling-enabled"]
        touchpad_settings['disable-while-typing'] = user_settings["disable-while-typing"]
        touchpad_settings['speed'] = user_settings["speed"]
        touchpad_settings['send-events'] = user_settings["send-events"]

    if user_settings := _GSettings("org.gnome.settings-daemon.plugins.power"):
        power_settings['power-button-action'] = user_settings['power-button-action']
        power_settings['auto-power-saver'] = user_settings['power-saver-profile-on-low-battery']
        power_settings['dim-screen'] = user_settings['idle-dim']
        power_settings['suspend-on-ac'] = user_settings['sleep-inactive-ac-type'] == 'suspend'
        power_settings['suspend-on-ac-delay'] = user_settings['sleep-inactive-ac-timeout'] / 60
        power_settings['suspend-on-battery'] = user_settings['sleep-inactive-battery-type'] == 'suspend'
        power_settings['suspend-on-battery-delay'] = user_settings['sleep-inactive-battery-timeout'] / 60

    if user_settings := _GSettings("org.gnome.desktop.session"):
        if user_settings['idle-delay']:
            power_settings['blank-screen'] = True
            power_settings['idle-delay'] = user_settings['idle-delay'] / 60
        else:
            power_settings['blank-screen'] = False

    if user_settings := _GSettings("org.gnome.settings-daemon.plugins.color"):
        night_light_settings['enabled'] = user_settings["night-light-enabled"]
        night_light_settings['schedule-automatic'] = user_settings["night-light-schedule-automatic"]
        night_light_settings['temperature'] = user_settings["night-light-temperature"]

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

    if user_settings := _GSettings("org.gnome.login-screen"):
        login_screen_settings['enable-welcome-message'] = user_settings["banner-message-enable"]
        login_screen_settings['welcome-message'] = user_settings["banner-message-text"]
        login_screen_settings['logo'] = user_settings["logo"]
        login_screen_settings['enable-logo'] = bool(user_settings["logo"])
        login_screen_settings['disable-restart-buttons'] = user_settings["disable-restart-buttons"]
        login_screen_settings['disable-user-list'] = user_settings["disable-user-list"]


def load_from_file(filename=None):
    config_parser = ConfigParser()

    try:
        if filename:
            logger.info(_("Importing from file '{filename}'").format(filename=filename))
            config_parser.read(filename)
        else:
            logger.info(_('Importing from standard input'))
            config_parser.read_file(sys.stdin)
    except ParsingError:
        logger.error(_('Failed to parse import file'))
        raise
    except UnicodeDecodeError:
        logger.error(_('Failed to read import file. Not encoded in UTF-8'))
        raise

    for settings in all_settings:
        section_name = settings.props.schema_id
        if section_name not in config_parser:
            logger.warn(_("Imported file does not have section '{section_name}'"
                          ).format(section_name=section_name))
            continue
        for key in settings:
            if key not in config_parser[section_name]:
                logger.warn(_("Imported file does not have key '{key_name}' in section '{section_name}'"
                              ).format(key_name=key, section_name=section_name))
                continue
            key_type = type(settings[key])
            if key_type == bool:
                settings[key] = config_parser.getboolean(section_name, key)
            else:
                settings[key] = key_type(config_parser[section_name][key])


def save_to_file(filename=None):
    config_parser = ConfigParser()

    for settings in all_settings:
        section_name = settings.props.schema_id
        config_parser[section_name] = {}
        for key in settings:
            config_parser[section_name][key] = str(settings[key])

    if filename:
        logger.info(_("Exporting to file '{filename}'").format(filename=filename))
        try:
            with open(filename, 'w') as outfile:
                config_parser.write(outfile)
        except PermissionError:
            logger.error(_("Cannot write to file '{filename}'. Permission denied"
                           ).format(filename=filename))
            raise
        except IsADirectoryError:
            logger.error(_("Cannot write to file '{filename}'. A directory with "
                            "the same name already exists"
                           ).format(filename=filename))
            raise
    else:
        logger.info(_('Exporting to standard output'))
        config_parser.write(sys.stdout)


def drop_unapplied_changes():
    '''Forget about changes that have not been applied yet'''
    for settings in all_settings:
        settings.revert()


def get_css() -> str:
    '''Get CSS for current settings (to append to theme's 'gnome-shell.css' resource)'''

    css = "\n\n/* 'GDM Settings' App Provided CSS */\n"

    ### Background ###
    background_type = BackgroundType[appearance_settings['background-type']]
    background_image = appearance_settings['background-image']
    adjustment_strat = appearance_settings['bg-adjustment']
    if background_type is BackgroundType.image and background_image:
        css += "\n"
        css += ".login-dialog { background: transparent; }\n"
        css += "#lockDialogGroup {\n"
        css += "  background-image: url('resource:///org/gnome/shell/theme/background');\n"
        if adjustment_strat == 'zoom':
            css += "  background-position: center;\n"
            css += "  background-size: cover;\n"
        else: # adjustment_strat == 'repeat':
            css += "  background-position: 0 0;\n"
            css += "  background-size: contain;\n"
            css += "  background-repeat: repeat;\n"
        css += "}\n"
    elif background_type is BackgroundType.color:
        background_color = appearance_settings['background-color']
        css += "\n"
        css += ".login-dialog { background: transparent; }\n"
        css += "#lockDialogGroup { background-color: " + background_color + "; }\n"

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
        css += "\n"
        css += select_elem("popup-menu-arrow") + " { width: 0px; }\n"
    # Rounded Corners
    if disable_rounded_corners:
        css += "\n"
        css +=  select_elem("panel-corner")
        css +=  " {\n"
        css += f"  -panel-corner-opacity: 0;\n"
        css +=  "}\n"
    # Text Color
    if change_text_color:
        css += "\n"
        css +=  select_elem('panel-button') + ",\n"
        css +=  select_elem('panel-button.clock-display') + " {\n"
        css += f"  color: {text_color};\n"
        css +=  "}\n"
    # Background Color
    if change_background_color:
        css += "\n"
        css +=  select_elem()
        css +=  " {\n"
        css += f"  background-color: {background_color};\n"
        css +=  "}\n"
        if not disable_rounded_corners:
            css += "\n"
            css +=  select_elem("panel-corner")
            css +=  " {\n"
            css += f"  -panel-corner-opacity: 1;\n"
            css += f"  -panel-corner-background-color: {background_color};\n"
            css +=  "}\n"

    # Large Welcome Message
    if (login_screen_settings['enable-welcome-message']
    and login_screen_settings['enlarge-welcome-message']):
        css += "\n"
        css += ".login-dialog-banner {\n"
        css += "  font-size: 1.5em;\n"
        css += "  font-weight: bold;\n"
        css += "}\n"

    return css


def _backup_default_shell_theme ():
    '''back up the default shell theme (if needed)'''

    logger.info(_("Backing up default shell theme …"))

    if gresource.is_unmodified(gresource.ShellGresourceFile):
        _commands.add(f"cp {gresource.ShellGresourceFile} {gresource.DefaultGresourceFile}")

    os.makedirs(env.TEMP_DIR, exist_ok=True)

    gresource.extract_default_theme(f'{env.TEMP_DIR}/default-pure')

    _commands.add(f"rm -rf {gresource.ThemesDir}/default-pure")
    _commands.add(f"mkdir -p {gresource.ThemesDir}")
    _commands.add(f"cp -r {env.TEMP_DIR}/default-pure -t {gresource.ThemesDir}")


def _gresource_apply():
    ''' Apply settings that require modification of 'gnome-shell-theme.gresource' file '''


    # If needed, back up the default shell theme

    pure_theme_not_exists = 'default-pure' not in shell_themes.theme_ids
    shell_gresource_is_stock = gresource.is_unmodified(gresource.ShellGresourceFile)

    if shell_gresource_is_stock or pure_theme_not_exists:
        _backup_default_shell_theme()


    # Apply shell theme settings

    theme_id = appearance_settings['shell-theme']
    theme_path = shell_themes.get_path(theme_id)
    shelldir   = os.path.join(theme_path, 'gnome-shell') if theme_path else None

    background_type = BackgroundType[appearance_settings['background-type']]
    background_image = None
    if background_type is BackgroundType.image:
        background_image = appearance_settings['background-image']

    compiled_file = gresource.compile(shelldir,
          additional_css=get_css(),
        background_image=background_image
    )


    # We need to copy the compiled gresource file instead of moving it because the
    # copy gets correct SELinux context/label where applicable and prevents breakage
    # of GDM in such situations.
    _commands.add(f"install -m644 {compiled_file} {gresource.ShellGresourceFile}")

    if gresource.UbuntuGdmGresourceFile:
        name_of_alternative = os.path.basename(gresource.UbuntuGdmGresourceFile)
        _commands.add('update-alternatives --quiet --install'
                      f' {gresource.UbuntuGdmGresourceFile}'
                      f' {name_of_alternative}'
                      f' {gresource.ShellGresourceFile}'
                      ' 0')

        _commands.add('update-alternatives --quiet --set'
                      f' {name_of_alternative}'
                      f' {gresource.ShellGresourceFile}')


def _dconf_apply():
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
        cursor_size = pointing_settings['cursor-size']
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
        gdm_conf_contents += f"cursor-size={cursor_size}\n"
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

        accessibility_menu = str(accessibility_settings['always-show-accessibility-menu']).lower()

        gdm_conf_contents +=  "#---- Accessibility ----\n"
        gdm_conf_contents +=  "[org/gnome/desktop/a11y]\n"
        gdm_conf_contents +=  "#------------------------\n"
        gdm_conf_contents += f"always-show-universal-access-status={accessibility_menu}\n"
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
        send_events = str(touchpad_settings['send-events']).lower()

        gdm_conf_contents +=  "#-------------- Touchpad ---------------\n"
        gdm_conf_contents +=  "[org/gnome/desktop/peripherals/touchpad]\n"
        gdm_conf_contents +=  "#---------------------------------------\n"
        gdm_conf_contents += f"speed={touchpad_speed}\n"
        gdm_conf_contents += f"tap-to-click={tap_to_click}\n"
        gdm_conf_contents += f"natural-scroll={natural_scrolling}\n"
        gdm_conf_contents += f"two-finger-scrolling-enabled={two_finger_scrolling}\n"
        gdm_conf_contents += f"disable-while-typing={disable_while_typing}\n"
        gdm_conf_contents += f"send-events='{send_events}'\n"
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

        logo_temp = os.path.join(env.TEMP_DIR, 'logo.temp')
        shutil.copy(logo_file, logo_temp)
        _commands.add(f"install -m644 '{logo_temp}' -T '{logo}'")

    overriding_files = get_overriding_files()
    if overriding_files:
        _commands.add('rm', *overriding_files)

    _commands.add(f"install -Dm644 '{temp_conf_path}' -t '{gdm_conf_dir}'")
    _commands.add(f"install -Dm644 '{temp_profile_path}' -T '{gdm_profile_path}'")
    _commands.add("dconf update")


def apply() -> bool:
    ''' Apply all settings '''

    _gresource_apply()
    _dconf_apply()

    result = _commands.run()

    if result:
        # When we change GDM shell theme it becomes the default theme but for the users
        # who didn't want to change shell theme for their session, we need to set it to a
        # pure/original version of the default shell theme
        # Note: We don't want to change user's shell theme if user set it explicitly to
        # default in order to match their GDM theme
        if user_settings := _GSettings('org.gnome.shell.extensions.user-theme'):
            if (user_settings['name'] == ''
            and main_settings["never-applied"]):
                user_settings['name'] = 'default-pure'

        main_settings["never-applied"] = False

        '''Save settings to GSettings of this app'''
        for settings in all_settings:
            settings.apply()

    return result


def apply_user_display_settings() -> bool:
    ''' Apply user's current display settings '''

    user_monitors_xml = os.path.join(env.XDG_CONFIG_HOME, 'monitors.xml')

    if not os.path.isfile(user_monitors_xml):
        raise FileNotFoundError(2, 'No such file or directory', user_monitors_xml)

    with open(user_monitors_xml) as monitors_xml:
        if monitors_xml.read() == '':
            raise FileNotFoundError(2, 'File is empty', user_monitors_xml)

    temp_monitors_xml = os.path.join(env.TEMP_DIR, 'monitors.xml')
    shutil.copyfile(user_monitors_xml, temp_monitors_xml)
    os.chmod(temp_monitors_xml, 0o644)

    _commands.add(['machinectl', 'shell', f'{gresource.GdmUsername}@', '/usr/bin/env',
                     'gsettings', 'set', 'org.gnome.mutter' 'experimental-features',
                     '"[\'scale-monitor-framebuffer\']"',
                     '&>/dev/null',
                   ])

    _commands.add(['install', '-Dm644',
                     '-o', gresource.GdmUsername,
                     temp_monitors_xml,
                     f'~{gresource.GdmUsername}/.config/monitors.xml',
                   ])

    return _commands.run()


def reset() -> bool:
    if gresource.UbuntuGdmGresourceFile:
        _commands.add(['update-alternatives',  '--quiet',  '--remove',
                          os.path.basename(gresource.UbuntuGdmGresourceFile),
                          gresource.ShellGresourceFile,
                       ])

    if os.path.exists(gresource.DefaultGresourceFile):
        _commands.add(['mv', '-f', gresource.DefaultGresourceFile, gresource.ShellGresourceFile])

    _commands.add("rm -f /etc/dconf/profile/gdm")
    _commands.add("rm -f /etc/dconf/db/gdm.d/95-gdm-settings")
    _commands.add("dconf update")

    if _commands.run():

        for settings in all_settings:
            for key in settings.props.settings_schema.list_keys():
                settings.reset(key)
            settings.apply()

        return True

    return False


def get_overriding_files():
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
