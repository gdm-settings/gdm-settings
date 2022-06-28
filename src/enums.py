'''Contains Enums used in the app'''

from enum import auto, Enum

class ZeroEnum (Enum):
    '''Enumeration whose values start from 0'''
    def _generate_next_value_(name, start, count, last_values):
        return Enum._generate_next_value_(name, 0, count, last_values)

class PackageType (ZeroEnum):
    Unknown  = auto()
    AppImage = auto()
    Flatpak  = auto()

class BackgroundType (ZeroEnum):
    none  = auto()
    image = auto()
    color = auto()

class AntiAliasing (ZeroEnum):
    grayscale = auto()
    rgba      = auto()
    none      = auto()

class FontHinting (ZeroEnum):
    full   = auto()
    medium = auto()
    slight = auto()
    none   = auto()

class MouseAcceleration (ZeroEnum):
    default  = auto()
    flat     = auto()
    adaptive = auto()
