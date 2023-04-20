'''Collection of convenience functions to bind widgets to Gio.Settings instances'''

from enum import Enum
from typing import Any, TypeVar
from collections.abc import Callable, Sequence

from gi.repository import GObject
from gi.repository import Gio
from gi.repository import Gdk
from gi.repository import Gtk
from gi.repository import Adw


default_flag = Gio.SettingsBindFlags.DEFAULT


__all__ = ['Settings']


def comborow_string_to_selected(string: str, comborow: Adw.ComboRow) -> int:
    string_list = comborow.get_model()
    for position, string_object in enumerate(string_list):
        if string == string_object.get_string():
            return position
    return 0

def comborow_selected_to_string(position: int, comborow: Adw.ComboRow) -> str:
    selected_item = comborow.get_selected_item()
    return selected_item.get_string()


def enum_name_to_value(name: str, enum: Enum) -> Any:
    return enum[name].value

def enum_value_to_name(value: Any, enum: Enum) -> str:
    return enum(value).name


def list_value_to_index_non_strict(value: Any, lyst: Sequence) -> int:
    try:
        return lyst.index(value)
    except ValueError:
        return 0

def list_value_to_index_strict (value: Any, lyst: Sequence) -> int:
    return lyst.index(value)

def list_index_to_value (index: int, lyst: Sequence) -> Any:
    return lyst[index]


def string_to_rgba(string: str, user_data=None) -> Gdk.RGBA:
    rgba = Gdk.RGBA()
    rgba.parse(string)
    return rgba

def rgba_to_string(rgba: Gdk.RGBA, user_data=None) -> str:
    return rgba.to_string()


class Settings(Gio.Settings):
    '''A wrapper around Gio.Settings for easy usage in Python'''

    __gtype_name__ = "Settings"

    def __init__(self, schema_id: str = None, **props):
        super().__init__(schema_id=schema_id, **props)

    @classmethod
    def new(cls, schema_id: str):
        return cls(schema_id)

    @classmethod
    def new_delayed(cls, schema_id: str):
        obj = cls(schema_id)
        obj.delay()
        return obj

    @classmethod
    def new_full(cls, schema: Gio.SettingsSchema, backend: Gio.SettingsBackend, path: str):
        return cls(settings_schema=schema, backend=backend, path=path)

    @classmethod
    def new_with_backend(cls, schema_id: str, backend: Gio.SettingsBackend):
        return cls(schema_id=schema_id, backend=backend)

    @classmethod
    def new_with_backend_and_path(cls, schema_id: str, backend: Gio.SettingsBackend, path: str):
        return cls(schema_id=schema_id, backend=backend, path=path)

    @classmethod
    def new_with_path(cls, schema_id: str, path: str):
        return cls(schema_id=schema_id, path=path)

    def bind (self, key: str, obj: GObject.Object, prop: str,
              flags: Gio.SettingsBindFlags = default_flag) -> None:
        super().bind(key, obj, prop, flags)

    def bind_to_colorbutton(self, key: str, colorbutton: Gtk.ColorButton,
                            flags: Gio.SettingsBindFlags = default_flag,
                            ) -> None:
        self.bind_with_mapping(key, colorbutton, 'rgba', flags,
                               string_to_rgba, rgba_to_string)

    def bind_to_comborow(self, key: str, comborow: Adw.ComboRow,
                         flags: Gio.SettingsBindFlags = default_flag,
                         ) -> None:
        self.bind_with_mapping(key, comborow, 'selected', flags,
                               comborow_string_to_selected,
                               comborow_selected_to_string,
                               comborow)

    def bind_via_enum(self, key: str, obj: GObject.Object, prop: str, enum: Enum,
                      flags: Gio.SettingsBindFlags = default_flag,
                      ) -> None:
        self.bind_with_mapping(key, obj, prop, flags,
                               enum_name_to_value,
                               enum_value_to_name,
                               enum)

    def bind_via_list(self, key: str, obj: GObject.Object, prop: str, lyst: Sequence,
                      flags: Gio.SettingsBindFlags = default_flag,
                      strict: bool = True) -> None:

        list_value_to_index = list_value_to_index_strict

        if not strict:
            list_value_to_index = list_value_to_index_non_strict

        self.bind_with_mapping(key, obj, prop, flags,
                               list_value_to_index,
                               list_index_to_value,
                               lyst)

    UserData = TypeVar("UserData")
    BindingKey = TypeVar("BindingKey")
    BindingProp = TypeVar("BindingProp")

    def bind_with_mapping(self, key: str, obj: GObject.Object, prop: str,
                          flags: Gio.SettingsBindFlags = default_flag,
                          key_to_prop: Callable[[BindingKey, UserData], BindingProp] = None,
                          prop_to_key: Callable[[BindingProp, UserData], BindingKey] = None,
                          user_data: UserData = None,
                          ) -> None:
        '''
        Recreate g_settings_bind_with_mapping since it does not exist in python bindings for Gio.Settings

        Taken directly from
        https://gitlab.gnome.org/GNOME/pygobject/uploads/bdd6ef6ee51a50f82d75673e43c1395b
        /0001-Implement-g_settings_bind_with_mapping-and-handle-ra.patch
        found in issue https://gitlab.gnome.org/GNOME/pygobject/-/issues/98
        '''

        self._ignore_key_changed = False

        def key_changed(self, key: str) -> None:
            if self._ignore_key_changed:
                return
            self._ignore_prop_changed = True
            obj.set_property(prop, key_to_prop(self[key], user_data))
            self._ignore_prop_changed = False

        def prop_changed(obj: GObject.Object, param: GObject.ParamSpec) -> None:
            if self._ignore_prop_changed:
                return
            self._ignore_key_changed = True
            self[key] = prop_to_key(obj.get_property(prop), user_data)
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
            obj.notify(prop)
            key_changed(self, key)
            if not (flags & Gio.SettingsBindFlags.GET_NO_CHANGES):
                self.connect('changed::' + key, key_changed)

        if flags & Gio.SettingsBindFlags.SET and prop_to_key:
            obj.connect('notify::' + prop, prop_changed)

        if not (flags & Gio.SettingsBindFlags.NO_SENSITIVITY):
            self.bind_writable(key, obj, "sensitive", False)
