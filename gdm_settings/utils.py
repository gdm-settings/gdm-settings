'''A self-contained collection of general purpose and reusable utilities
(functions & classes)

'self-contained' means that this module does not depend on anything from
the gdm_settings package'''

import os
import subprocess

from enum import Enum
from typing import Any, Optional, TypeVar
from collections.abc import Callable, Iterator, Sequence


from gi.repository import Adw
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import Gio
from gi.repository import GObject


def get_stdout(command: str | list [str],
               /, *,
               decode: bool = True,
               ) -> str | bytes:
    '''get standard output of a command'''

    if isinstance(command, str):
        command = command.split()

    stdout = subprocess.run(command, stdout=subprocess.PIPE).stdout

    if decode:
        stdout = stdout.decode()

    return stdout


def list_files(dir_path: str,
               base: Optional[str] = None,
               *,
               recursive: bool = True,
               ) -> Iterator[str]:
    """list files (only) inside a directory"""

    if base is None:
        base = dir_path

    for child in os.listdir(dir_path):
        child_path = os.path.join(dir_path, child)

        if not os.path.isdir(child_path):
            yield os.path.relpath(child_path, base)
        elif recursive:
            yield from list_files(child_path, base)


def GProperty(type: GObject.GType,
              default: Optional[object] = None,
              *args,
              readable: bool = True,
              writable: bool = True,
              construct: bool = False,
              construct_only: bool = False,
              additional_flags: GObject.ParamFlags = GObject.ParamFlags(0),
              **kwargs,
              ) -> GObject.Property:
    '''A wrapper around GObject.Property decorator

    Provides shorter syntax for creating GObject properties.
    '''

    flags = additional_flags
    if readable:
        flags |= GObject.ParamFlags.READABLE
    if writable:
        flags |= GObject.ParamFlags.WRITABLE
    if construct:
        flags |= GObject.ParamFlags.CONSTRUCT
    if construct_only:
        flags |= GObject.ParamFlags.CONSTRUCT_ONLY

    return GObject.Property(*args, type=type, default=default, flags=flags, **kwargs)


Callback = Callable[[], Any]

class InvalidGioTaskError (Exception): pass
class AlreadyRunningError (Exception): pass


class BackgroundTask (GObject.Object):
    __gtype_name__ = 'BackgroundTask'

    def __init__ (self, function: Callback, finish_callback: Callback):
        super().__init__()

        self.function = function
        self.finish_callback = finish_callback
        self._current = None

    def start(self) -> None:
        if self._current:
            AlreadyRunningError('Task is already running')

        finish_callback = lambda self, task, nothing: self.finish_callback()

        task = Gio.Task.new(self, None, finish_callback, None)
        task.run_in_thread(self._thread_cb)

        self._current = task

    @staticmethod
    def _thread_cb (task: Gio.Task, self, task_data: object, cancellable: Gio.Cancellable):
        try:
            retval = self.function()
            task.return_value(retval)
        except Exception as e:
            task.return_value(e)

    def finish (self):
        task = self._current
        self._current = None

        if not Gio.Task.is_valid(task, self):
            raise InvalidGioTaskError()

        value = task.propagate_value().value

        if isinstance(value, Exception):
            raise value

        return value


class _MappingFuncs:
    '''A collection of functions for 'GSettings' class that convert values
    from Settings keys to GObject properties and vice versa.'''

    class RGBA:
        def from_string(string: str, user_data=None) -> Gdk.RGBA:
            rgba = Gdk.RGBA()
            rgba.parse(string)
            return rgba

        def to_string(rgba: Gdk.RGBA, user_data=None) -> str:
            return rgba.to_string()

    class ComboRow:
        def string_to_selected(string: str, comborow: Adw.ComboRow) -> int:
            string_list = comborow.get_model()
            for position, string_object in enumerate(string_list):
                if string == string_object.get_string():
                    return position
            return 0

        def selected_to_string(position: int, comborow: Adw.ComboRow) -> str:
            selected_item = comborow.get_selected_item()
            return selected_item.get_string()

    class Enum:
        def name_to_value(name: str, enum: Enum) -> Any:
            return enum[name].value

        def value_to_name(value: Any, enum: Enum) -> str:
            return enum(value).name

    class List:
        def value_to_index_non_strict(value: Any, lyst: Sequence) -> int:
            try:
                return lyst.index(value)
            except ValueError:
                return 0

        def value_to_index_strict (value: Any, lyst: Sequence) -> int:
            return lyst.index(value)

        def index_to_value (index: int, lyst: Sequence) -> Any:
            return lyst[index]


class GSettings(Gio.Settings):
    '''A wrapper around Gio.Settings for easy usage in Python'''

    __gtype_name__ = "_Settings"    # "GSettings" name is not available
    _default_flag = Gio.SettingsBindFlags.DEFAULT

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
              flags: Gio.SettingsBindFlags = _default_flag) -> None:
        super().bind(key, obj, prop, flags)

    def bind_to_colorbutton(self, key: str, colorbutton: Gtk.ColorButton,
                            flags: Gio.SettingsBindFlags = _default_flag,
                            ) -> None:
        self.bind_with_mapping(key, colorbutton, 'rgba', flags,
                               _MappingFuncs.RGBA.from_string,
                               _MappingFuncs.RGBA.to_string)

    def bind_to_comborow(self, key: str, comborow: Adw.ComboRow,
                         flags: Gio.SettingsBindFlags = _default_flag,
                         ) -> None:
        self.bind_with_mapping(key, comborow, 'selected', flags,
                               _MappingFuncs.ComboRow.string_to_selected,
                               _MappingFuncs.ComboRow.selected_to_string,
                               comborow)

    def bind_via_enum(self, key: str, obj: GObject.Object, prop: str, enum: Enum,
                      flags: Gio.SettingsBindFlags = _default_flag,
                      ) -> None:
        self.bind_with_mapping(key, obj, prop, flags,
                               _MappingFuncs.Enum.name_to_value,
                               _MappingFuncs.Enum.value_to_name,
                               enum)

    def bind_via_list(self, key: str, obj: GObject.Object, prop: str, lyst: Sequence,
                      flags: Gio.SettingsBindFlags = _default_flag,
                      strict: bool = True) -> None:

        value_to_index = _MappingFuncs.List.value_to_index_strict
        index_to_value = _MappingFuncs.List.index_to_value

        if not strict:
            value_to_index = _MappingFuncs.List.value_to_index_non_strict

        self.bind_with_mapping(key, obj, prop, flags,
                               value_to_index,
                               index_to_value,
                               lyst)

    UserData = TypeVar("UserData")
    BindingKey = TypeVar("BindingKey")
    BindingProp = TypeVar("BindingProp")

    def bind_with_mapping(self, key: str, obj: GObject.Object, prop: str,
                          flags: Gio.SettingsBindFlags = _default_flag,
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