from gi.repository import Gio
from gi.repository import GObject

from typing import Any
from collections.abc import Callable

Callback = Callable[[], Any]

__all__ = ['InvalidGioTaskError', 'AlreadyRunningError', 'BackgroundTask']


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
