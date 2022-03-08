# Login Manager Settings (gdm-settings)

An app to change settings of Gnome's Display/Login Manager.

It is written in Python and provides a Graphical interface using GTK+ and LibAdwaita.

<img src="screenshots/screenshot-1.png#gh-light-mode-only" alt="screenshot" width=100%/><img src="screenshots/screenshot-1-dark.png#gh-dark-mode-only" alt="screenshot" width=100%/>

<center><a href="screenshots/README.md">More Screenshots</a></center>

## Important Note! (Alpha-Stage Software)

This app is in an early stage of development (it is mostly feature complete). It may crash frequently.

## How to Install?

### Package Installation

#### On Arch/Manjaro

This app is available in the AUR as [gdm-settings](https://aur.archlinux.org/packages/gdm-settings) and [gdm-settings-git](https://aur.archlinux.org/packages/gdm-settings-git). You can install it using your favorite AUR helper. For example,

````bash
yay -S gdm-settings-git
````

or

```bash
paru -S gdm-settings-git
```

or

```bash
pamac install gdm-settings
```

**Note:**  I recommend installing `gdm-settings-git` instead of regular `gdm-settings` package because in this stage of development, `gdm-settings-git`, having new fixes included, may be more reliable (relatively).

### Manual Installation

First of all, make sure all build-time and run-time dependencies are installed

#### Method 1

1. Download and extract this [zip file](https://github.com/realmazharhussain/gdm-settings/archive/refs/heads/main.zip) (or this [tar.gz file](https://github.com/realmazharhussain/gdm-settings/archive/refs/heads/main.tar.gz))
1. Go to the folder where you extracted that file
1. Open your terminal application in that folder
1. Type `meson build` and press Enter
1. Type `meson install -C build` and press Enter
1. Type your password and press Enter

#### Method 2

First, make sure git is installed on your system then run the following commands in the terminal

```bash
git clone --depth=1 --single-branch https://github.com/realmazharhussain/gdm-settings
cd gdm-settings
meson build
meson install -C build
```

## Dependencies

### Run-time Dependencies

- [LibAdwaita](https://gnome.pages.gitlab.gnome.org/libadwaita)
- [GLib](https://gitlab.gnome.org/GNOME/glib)
- [PyGObject](https://pygobject.readthedocs.io)

### Build-time Dependencies

- [Meson](https://mesonbuild.com) (v0.58 or newer)
- [Blueprint Compiler](https://jwestman.pages.gitlab.gnome.org/blueprint-compiler) (latest) (Do not install it manually)

**Note:** Blueprint Compiler will automatically be downloaded and configured for this app

### How to install dependencies?

You need to run the following commands in terminal to install the dependencies

#### On Debian/Ubuntu

**Note:** LibAdwaita (libadwaita-1-dev) will only be available in Debian 12 and Ubuntu 22.04 or later

```bash
sudo apt install libadwaita-1-dev libglib2.0-dev python-gi-dev #Runtime Dependencies
sudo apt install meson #Build Dependencies
```

#### On Arch/Manjaro

```bash
sudo pacman -S libadwaita glib2 python-gobject #Runtime Dependencies
sudo pacman -S meson #Build Dependencies
```

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

