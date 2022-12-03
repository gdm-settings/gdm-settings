'''Setup logging'''

import logging


red = '\033[31m'
bold = '\033[1m'
blue = '\033[34m'
green = '\033[32m'
normal = '\033[0m'
yellow = '\033[33m'
magenta = '\033[35m'
bright_red = '\033[91m'

class ColoredFormatter (logging.Formatter):
    def format (self, record):
        match record.levelname:
            case 'CRITICAL': level_color = bright_red
            case 'ERROR':    level_color = red
            case 'WARNING':  level_color = yellow
            case 'INFO':     level_color = green
            case default:    level_color = blue

        return (bold + level_color + record.levelname + ':' + normal
                + ' ' + record.getMessage())


logging.root.setLevel(logging.DEBUG)

stderr_handler = logging.StreamHandler()
stderr_handler.setFormatter(ColoredFormatter())
# FIXME: logging level of stderr_handler can be changed only
# if we set it to a high value here
stderr_handler.setLevel(60)
logging.root.addHandler(stderr_handler)

#logging.basicConfig(format=f'{style_bold}%(levelname)s:{style_normal} %(message)s')
