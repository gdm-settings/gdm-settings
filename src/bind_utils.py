'''Collection of convenience functions to bind widgets to Gio.Settings instances'''

from gi.repository import Gio
from gi.repository import Gdk


default_flag = Gio.SettingsBindFlags.DEFAULT


def bind (settings, key, widget, property, flags=default_flag):
    settings.bind(key, widget, property, flags)


def comborow_string_to_selected(string, comborow):
    string_list = comborow.get_model()
    for position, string_object in enumerate(string_list):
        if string == string_object.get_string():
            return position
    return 0

def comborow_selected_to_string(position, comborow):
    selected_item = comborow.get_selected_item()
    return selected_item.get_string()

def bind_comborow(comborow, settings, key, flags=default_flag):
    bind_with_mapping(settings, key, comborow, 'selected', flags,
                      comborow_string_to_selected,
                      comborow_selected_to_string,
                      comborow,
                      )


def enum_name_to_value(name, enum):
    return enum[name].value

def enum_value_to_name(value, enum):
    return enum(value).name

def bind_by_enum(settings, key, widget, property, enum, flags=default_flag):
    bind_with_mapping(settings, key, widget, property, flags,
                      enum_name_to_value,
                      enum_value_to_name,
                      enum,
                      )

def bind_comborow_by_enum(comborow, settings, key, enum, flags=default_flag):
    bind_by_enum(settings, key, comborow, 'selected', enum, flags)


def list_value_to_index (value, lyst):
    return lyst.index(value)

def list_index_to_value (index, lyst):
    return lyst[index]

def bind_comborow_by_list(comborow, settings, key, lyst, flags=default_flag):
    bind_with_mapping(settings, key, comborow, 'selected', flags,
                      list_value_to_index,
                      list_index_to_value,
                      lyst,
                      )


def string_to_rgba(string, colorbutton):
    rgba = Gdk.RGBA()
    rgba.parse(string)
    return rgba

def rgba_to_string(rgba, colorbutton):
    return rgba.to_string()

def bind_colorbutton(colorbutton, settings, key, flags=default_flag):
    bind_with_mapping(settings, key, colorbutton, 'rgba', flags,
                      string_to_rgba,
                      rgba_to_string,
                      )


def bind_with_mapping(settings, key, widget, prop, flags=None, key_to_prop=None, prop_to_key=None, user_data=None):
    '''
    Recreate g_settings_bind_with_mapping since it does not exist in python bindings for Gio.Settings

    Taken directly from
    https://gitlab.gnome.org/GNOME/pygobject/uploads/bdd6ef6ee51a50f82d75673e43c1395b
    /0001-Implement-g_settings_bind_with_mapping-and-handle-ra.patch
    found in issue https://gitlab.gnome.org/GNOME/pygobject/-/issues/98
    '''

    settings._ignore_key_changed = False

    def key_changed(settings, key):
        if settings._ignore_key_changed:
            return
        settings._ignore_prop_changed = True
        widget.set_property(prop, key_to_prop(settings[key], user_data))
        settings._ignore_prop_changed = False

    def prop_changed(widget, param):
        if settings._ignore_prop_changed:
            return
        settings._ignore_key_changed = True
        settings[key] = prop_to_key(widget.get_property(prop), user_data)
        settings._ignore_key_changed = False

    if not (key_to_prop or prop_to_key):
        raise ValueError('at least one of key_to_prop and prop_to_key should be not None')

    if key_to_prop and not callable(key_to_prop):
        TypeError(f"'{type(key_to_prop)}' object is not callable")

    if prop_to_key and not callable(prop_to_key):
        TypeError(f"'{type(prop_to_key)}' object is not callable")

    if flags & Gio.SettingsBindFlags.INVERT_BOOLEAN:
        raise ValueError('Gio.Settings.bind_with_mapping does not support'
                         ' flag Gio.SettingsBindFlags.INVERT_BOOLEAN')

    if not flags & (flags & Gio.SettingsBindFlags.GET | flags & Gio.SettingsBindFlags.SET):
        flags |= Gio.SettingsBindFlags.GET | flags & Gio.SettingsBindFlags.SET

    if flags & Gio.SettingsBindFlags.GET and key_to_prop:
        key_changed(settings, key)
        if not (flags & Gio.SettingsBindFlags.GET_NO_CHANGES):
            settings.connect('changed::' + key, key_changed)

    if flags & Gio.SettingsBindFlags.SET and prop_to_key:
        widget.connect('notify::' + prop, prop_changed)

    if not (flags & Gio.SettingsBindFlags.NO_SENSITIVITY):
        settings.bind_writable(key, widget, "sensitive", False)
