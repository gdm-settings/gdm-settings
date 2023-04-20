'''Contains Enums used in the app'''

from enum import Enum, auto


class PackageType (Enum):
    Unknown  = auto()
    AppImage = auto()
    Flatpak  = auto()


class BackgroundType (Enum):
    default = 0
    image   = 1
    color   = 2
