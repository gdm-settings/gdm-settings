import os
import sys
import gettext
import locale

from . import config


# This app is relocatable. APP_DIR (detected during runtime) is path
# to the base directory in which this app is running from.
# For example, /opt/gdm-settings, /tmp/.mount_GDM_Se1tvOjd, etc.
APP_DIR = os.path.realpath(__file__).split(config.PREFIX)[0]

# Prefer the data dir where the app is installed over other data dirs
_data_dirs = os.environ.get('XDG_DATA_DIRS', '/usr/local/share:/usr/share').split(':')
_app_data_dir = APP_DIR + config.DATA_DIR
if _app_data_dir in _data_dirs:
    _data_dirs.remove(_app_data_dir)
os.environ['XDG_DATA_DIRS'] = ':'.join([_app_data_dir, *_data_dirs])

_localedir = APP_DIR + config.LOCALE_DIR
locale.bindtextdomain("gdm-settings", _localedir)
locale.textdomain("gdm-settings")
gettext.bindtextdomain('gdm-settings', _localedir)
gettext.textdomain('gdm-settings')

def main() -> int:
    from .app import GdmSettingsApp
    app = GdmSettingsApp()
    
    try:
        return app.run(sys.argv)
    except KeyboardInterrupt:
        return 0

if __name__ == '__main__':
    sys.exit(main())
