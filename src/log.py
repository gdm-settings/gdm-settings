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
        if record.levelname == 'CRITICAL':
            color = bright_red
        elif record.levelname == 'ERROR':
            color = red
        elif record.levelname == 'WARNING':
            color = yellow
        elif record.levelname == 'INFO':
            color = green
        else:
            color = blue

        return bold + color + record.levelname + magenta + '::' + normal + record.getMessage()


logging.root.setLevel(logging.DEBUG)

stderr_handler = logging.StreamHandler()
stderr_handler.setFormatter(ColoredFormatter())
# FIXME: logging level of stderr_handler can be changed only
# if we set it to a high value here
stderr_handler.setLevel(60)
logging.root.addHandler(stderr_handler)

#logging.basicConfig(format=f'{style_bold}%(levelname)s:{style_normal} %(message)s')
