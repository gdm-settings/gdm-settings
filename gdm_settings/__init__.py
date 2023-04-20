import os
import sys
import gettext
import locale

from gettext import gettext as _

from . import config

# This app is relocatable. APP_DIR (detected during runtime) is path
# to the base directory in which this app is running from.
# For example, /opt/gdm-settings, /tmp/.mount_GDM_Se1tvOjd, etc.
APP_DIR = os.path.realpath(__file__).split(config.prefix)[0]

_localedir = APP_DIR + config.localedir
locale.bindtextdomain("gdm-settings", _localedir)
locale.textdomain("gdm-settings")
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
resource_base_path = '/app/'


def main() -> int:
    from .app import GdmSettingsApp
    app = GdmSettingsApp()
    
    try:
        return app.run(sys.argv)
    except KeyboardInterrupt:
        return 0

if __name__ == '__main__':
    sys.exit(main())
