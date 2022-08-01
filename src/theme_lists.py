'''Contains lists of themes'''

shell_themes  = []
sound_themes  = []
icon_themes   = []
cursor_themes = []

class Theme:
    def __init__(self, name:str, path:str):
        self.name = name
        self.path = path
    def __lt__(self, value, /):
        return self.name.casefold() < value.name.casefold()
    def __repr__(self):
        return f"Theme(name='{self.name}', path='{self.path}')"

def update_theme_list(theme_type:str, /):
    temp_list = []

    if theme_type == 'shell':
        dirname = 'themes'
        decider = 'gnome-shell'
        temp_list.append(Theme('default', None))
    elif theme_type == 'sound':
        dirname = 'sounds'
        decider = 'index.theme'
    elif theme_type == 'icon':
        dirname = 'icons'
        decider = 'index.theme'
    elif theme_type == 'cursor':
        dirname = 'icons'
        decider = 'cursors'
    else:
        raise ValueError(f"invalid theme_type '{theme_type}'")

    from os import path
    from glob import glob
    from .env import HOST_ROOT, HOST_DATA_DIRS
    for data_dir in HOST_DATA_DIRS:
        for theme_dir in glob(f"{HOST_ROOT}{data_dir}/{dirname}/*"):
            theme_name = path.basename(theme_dir)
            if path.exists(path.join(theme_dir, decider)) and theme_name not in [theme.name for theme in temp_list]:
                temp_list.append(Theme(theme_name, theme_dir))

    if theme_type == 'shell':
        global shell_themes
        shell_themes = sorted(temp_list)
    elif theme_type == 'sound':
        global sound_themes
        sound_themes = sorted(temp_list)
    elif theme_type == 'icon':
        global icon_themes
        icon_themes = sorted(temp_list)
    elif theme_type == 'cursor':
        global cursor_themes
        cursor_themes = sorted(temp_list)

def update_all_theme_lists():
    for theme_type in 'shell', 'icon', 'cursor', 'sound':
        update_theme_list(theme_type)

update_all_theme_lists()
