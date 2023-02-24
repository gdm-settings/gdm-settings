'''Collection of convenience functions to bind widgets to Gio.Settings instances'''

from gi.repository import Gio
from gi.repository import Gdk


default_flag = Gio.SettingsBindFlags.DEFAULT


__all__ = ['Settings']


def comborow_string_to_selected(string, comborow):
    string_list = comborow.get_model()
    for position, string_object in enumerate(string_list):
        if string == string_object.get_string():
            return position
    return 0

def comborow_selected_to_string(position, comborow):
    selected_item = comborow.get_selected_item()
    return selected_item.get_string()


def enum_name_to_value(name, enum):
    return enum[name].value

def enum_value_to_name(value, enum):
    return enum(value).name


def list_value_to_index_non_strict(value, lyst):
    try:
        return lyst.index(value)
    except ValueError:
        return 0

def list_value_to_index_strict (value, lyst):
    return lyst.index(value)

def list_index_to_value (index, lyst):
    return lyst[index]


def string_to_rgba(string, colorbutton):
    rgba = Gdk.RGBA()
    rgba.parse(string)
    return rgba

def rgba_to_string(rgba, colorbutton):
    return rgba.to_string()


class Settings(Gio.Settings):
    '''A wrapper around Gio.Settings for easy usage in Python'''

    __gtype_name__ = "Settings"

    def __init__(self, schema_id:str=None, **props):
        super().__init__(schema_id=schema_id, **props)

    @classmethod
    def new(cls, schema_id:str):
        return cls(schema_id)

    @classmethod
    def new_delayed(cls, schema_id:str):
        obj = cls(schema_id)
        obj.delay()
        return obj

    @classmethod
    def new_full(cls, schema:Gio.SettingsSchema, backend:Gio.SettingsBackend, path:str):
        return cls(settings_schema=schema, backend=backend, path=path)

    @classmethod
    def new_with_backend(cls, schema_id:str, backend:Gio.SettingsBackend):
        return cls(schema_id=schema_id, backend=backend)

    @classmethod
    def new_with_backend_and_path(cls, schema_id:str, backend:Gio.SettingsBackend, path:str):
        return cls(schema_id=schema_id, backend=backend, path=path)

    @classmethod
    def new_with_path(cls, schema_id:str, path:str):
        return cls(schema_id=schema_id, path=path)

    def bind (self, key, widget, prop, flags=default_flag):
        super().bind(key, widget, prop, flags)

    def bind_to_colorbutton(self, key, colorbutton, flags=default_flag):
        self.bind_with_mapping(key, colorbutton, 'rgba', flags,
                               string_to_rgba, rgba_to_string)

    def bind_to_comborow(self, key, comborow, flags=default_flag):
        self.bind_with_mapping(key, comborow, 'selected', flags,
                               comborow_string_to_selected,
                               comborow_selected_to_string,
                               comborow)

    def bind_via_enum(self, key, widget, prop, enum, flags=default_flag):
        self.bind_with_mapping(key, widget, prop, flags,
                               enum_name_to_value,
                               enum_value_to_name,
                               enum)

    def bind_via_list(self, key, widget, prop, lyst, flags=default_flag, strict=True):
        list_value_to_index = list_value_to_index_strict

        if not strict:
            list_value_to_index = list_value_to_index_non_strict

        self.bind_with_mapping(key, widget, prop, flags,
                               list_value_to_index,
                               list_index_to_value,
                               lyst)

    def bind_with_mapping(self, key, widget, prop, flags=default_flag,
                          key_to_prop=None, prop_to_key=None, user_data=None):
        '''
        Recreate g_settings_bind_with_mapping since it does not exist in python bindings for Gio.Settings

        Taken directly from
        https://gitlab.gnome.org/GNOME/pygobject/uploads/bdd6ef6ee51a50f82d75673e43c1395b
        /0001-Implement-g_settings_bind_with_mapping-and-handle-ra.patch
        found in issue https://gitlab.gnome.org/GNOME/pygobject/-/issues/98
        '''

        self._ignore_key_changed = False

        def key_changed(self, key):
            if self._ignore_key_changed:
                return
            self._ignore_prop_changed = True
            widget.set_property(prop, key_to_prop(self[key], user_data))
            self._ignore_prop_changed = False

        def prop_changed(widget, param):
            if self._ignore_prop_changed:
                return
            self._ignore_key_changed = True
            self[key] = prop_to_key(widget.get_property(prop), user_data)
            self._ignore_key_changed = False

        if not (key_to_prop or prop_to_key):
            raise ValueError('at least one of key_to_prop and prop_to_key should be not None')

        if key_to_prop and not callable(key_to_prop):
            TypeError(f"'{type(key_to_prop)}' object is not callable")

        if prop_to_key and not callable(prop_to_key):
            TypeError(f"'{type(prop_to_key)}' object is not callable")

        if flags & Gio.SettingsBindFlags.INVERT_BOOLEAN:
            raise ValueError('Gio.Settings.bind_with_mapping does not support'
                             ' flag Gio.SettingsBindFlags.INVERT_BOOLEAN')

        if not (flags & Gio.SettingsBindFlags.GET or flags & Gio.SettingsBindFlags.SET):
            flags |= Gio.SettingsBindFlags.GET |  Gio.SettingsBindFlags.SET

        if flags & Gio.SettingsBindFlags.GET and key_to_prop:
            widget.notify(prop)
            key_changed(self, key)
            if not (flags & Gio.SettingsBindFlags.GET_NO_CHANGES):
                self.connect('changed::' + key, key_changed)

        if flags & Gio.SettingsBindFlags.SET and prop_to_key:
            widget.connect('notify::' + prop, prop_changed)

        if not (flags & Gio.SettingsBindFlags.NO_SENSITIVITY):
            self.bind_writable(key, widget, "sensitive", False)
