# Login Manager Settings (gdm-settings)

An app to change settings of Gnome's Display/Login Manager.

It is written in Python and provides a Graphical interface using GTK+ and LibAdwaita.

<img src="screenshots/screenshot-1.png#gh-light-mode-only" alt="screenshot" width=100%/><img src="screenshots/screenshot-1-dark.png#gh-dark-mode-only" alt="screenshot" width=100%/>

<center><a href="screenshots/README.md">More Screenshots</a></center>

## Important Note! (Alpha-Stage Software)

This app is in an early stage of development (it is mostly feature complete). It may crash frequently.

## How to Install?

### Manual Installation

0. Make sure all build-time and run-time dependencies are installed
1. Download and extract this [zip file](https://github.com/realmazharhussain/gdm-settings/archive/refs/heads/main.zip) (or this [tar.gz file](https://github.com/realmazharhussain/gdm-settings/archive/refs/heads/main.tar.gz))\
   OR\
   Clone this repository. You can do so with the command `git clone --depth=1 --singe-branch https://github.com/realmazharhussain/gdm-settings`
2. Go to the folder where you extracted/cloned this file/repo
3. Open your terminal application in that folder
4. Type `meson build` and press Enter
5. Type `meson install -C build` and press Enter
5. Type your password and press Enter

### Arch-based distros

This app is available in the AUR as [gdm-settings](https://aur.archlinux.org/packages/gdm-settings) and [gdm-settings-git](https://aur.archlinux.org/packages/gdm-settings-git). You can install it using your favorite AUR helper.

## Dependencies

### Run-time Dependencies

- LibAdwaita-1
- Glib-2 (development version)
- python-gobject a.k.a PyGObject

### Build-time Dependencies

- Meson
- Blueprint Compiler

## Features

- Import user/session settings
- Change Background/Wallpaper (Image/Color)
- Apply themes
  - Shell
  - Icon
  - Cursor
  - Sound
- Font Settings
  - Font
  - Antialiasing
  - Hinting
  - Scaling
- Top Bar Settings
  - Disable arrows
  - Disable rounded corners
  - Change text color
  - Change background color
  - Show/Hide weekday, seconds, battery percentage
  - Clock format (AM/PM or 24h)
- Sound Settings
  - Raise volume over 100%
  - Event sounds
  - Input feedback sounds
- Touchpad settings
  - Speed
  - Tap to Click
  - Natural Scrolling
  - Two-finger scrolling
- Night light settings
  - Enable/Disable
  - Automatic/Manual Schedule
  - Temperature
- Miscellaneous Settings
  - Welcome Message
  - Logo
  - Disable restart buttons
  - Disable user list

## Planned Features

- Set a gradient as the background
- Apply blur effect to the background image
- A command-line interface
- Tab-completion for the command-line interface

