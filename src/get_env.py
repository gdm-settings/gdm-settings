from os import environ as env
from .utils import PATH

HOME = env.get('HOME')
XDG_CACHE_HOME = env.get('XDG_CACHE_HOME', f"{HOME}/.cache")
SYSTEM_DATA_DIRS = PATH(env.get('SYSTEM_DATA_DIRS', '/usr/local/share:/usr/share'))
