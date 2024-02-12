'''Python package for GDM Settings app'''

import os
import sys
import gettext
import locale
import logging
import tempfile
from enum import Enum

from gettext import gettext as _

import gi
gi.require_version('Adw', '1')

from . import config

# This app is relocatable. APP_DIR (detected during runtime) is path
# to the base directory in which this app is running from.
# For example, /opt/gdm-settings, /tmp/.mount_GDM_Se1tvOjd, etc.
APP_DIR = os.path.realpath(__file__).split(config.prefix)[0]

_localedir = APP_DIR + config.localedir
locale.bindtextdomain('gdm-settings', _localedir)
locale.textdomain('gdm-settings')
gettext.bindtextdomain('gdm-settings', _localedir)
gettext.textdomain('gdm-settings')

# Prefer the data dir where the app is installed over other data dirs
_data_dirs = os.environ.get('XDG_DATA_DIRS', '/usr/local/share:/usr/share').split(':')
_app_data_dir = APP_DIR + config.datadir
if _app_data_dir in _data_dirs:
    _data_dirs.remove(_app_data_dir)
os.environ['XDG_DATA_DIRS'] = ':'.join([_app_data_dir, *_data_dirs])

APP_ID = 'io.github.realmazharhussain.GdmSettings'
APP_NAME = _('GDM Settings')
PROJECT_NAME = 'gdm-settings'

VERSION = config.version
BUILD_TYPE = config.buildtype
APP_DATA_DIR = APP_DIR + config.datadir + '/' + PROJECT_NAME


# Set up logging

class _Style(str, Enum):
    RED = '\033[31m'
    BOLD = '\033[1m'
    BLUE = '\033[34m'
    GREEN = '\033[32m'
    NORMAL = '\033[0m'
    YELLOW = '\033[33m'
    MANENTA = '\033[35m'
    BRIGHT_RED = '\033[91m'


class _StdErrFormatter(logging.Formatter):
    def format (self, record):
        match record.levelname:
            case 'CRITICAL': level_color = _Style.BRIGHT_RED
            case 'ERROR':    level_color = _Style.RED
            case 'WARNING':  level_color = _Style.YELLOW
            case 'INFO':     level_color = _Style.GREEN
            case default:    level_color = _Style.BLUE

        return (_Style.BOLD + level_color + record.levelname + _Style.NORMAL + ':'
                + _Style.MANENTA + record.name + _Style.NORMAL + ':'
                + ' ' + record.getMessage())


logger = logging.getLogger(__name__)

logger.setLevel(logging.DEBUG)

# FIXME: logging level of handlers can be changed only
# if we set it to a high value here

stderr_log_handler = logging.StreamHandler()
stderr_log_handler.setFormatter(_StdErrFormatter())
stderr_log_handler.setLevel(logging.DEBUG)
logger.addHandler(stderr_log_handler)


def main() -> int:
    from .gui import GdmSettingsApp
    gui = GdmSettingsApp()
    
    try:
        return gui.run(sys.argv)
    except KeyboardInterrupt:
        return 0
