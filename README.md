# Login Manager Settings (gdm-settings)

An app to change settings of Gnome's Display/Login Manager.

It is written in Python and provides a Graphical interface using GTK+ and LibAdwaita.

<img src="screenshots/screenshot-1.png#gh-light-mode-only" alt="screenshot" width=100%/><img src="screenshots/screenshot-1-dark.png#gh-dark-mode-only" alt="screenshot" width=100%/>

- [Screenshots](screenshots/README.md)
- [Features](docs/features.md)

## Important Note! (Alpha-Stage Software)

This app is in an early stage of development (but mostly feature complete). There may be some weirdness here and there.

## How to Install?

### On Arch/Manjaro

This app is available in the AUR as [gdm-settings](https://aur.archlinux.org/packages/gdm-settings) and [gdm-settings-git](https://aur.archlinux.org/packages/gdm-settings-git) (recommended). You can install it using your favorite AUR helper. For example,

````bash
yay -S gdm-settings-git
````

or

```bash
paru -S gdm-settings-git
```

or

```bash
pamac install gdm-settings-git
```

**Note:**  I recommend installing `gdm-settings-git` instead of regular `gdm-settings` package because in this stage of development, `gdm-settings-git`, having new fixes included, may have fewer issues (relatively).

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
git clone --depth=1 https://github.com/realmazharhussain/gdm-settings
cd gdm-settings
meson build
meson install -C build
```

## Dependencies

### Run-time Dependencies

- [LibAdwaita](https://gnome.pages.gitlab.gnome.org/libadwaita)
- [GLib](https://gitlab.gnome.org/GNOME/glib)
- [PyGObject](https://pygobject.readthedocs.io)
- [GetText](https://www.gnu.org/software/gettext)

### Build-time Dependencies

- [Meson](https://mesonbuild.com) (v0.58 or newer)
- [Blueprint Compiler](https://jwestman.pages.gitlab.gnome.org/blueprint-compiler) (latest) (No need to install it manually)
- [GObject Introspection](https://gi.readthedocs.io) (required for 'Blueprint Compiler' to work correctly)

**Note:** Blueprint Compiler will automatically be downloaded and configured (only) for this app

### How to install dependencies?

You need to run the following commands in terminal to install the dependencies

#### On Debian/Ubuntu

**Note:** LibAdwaita (libadwaita-1-dev) will only be available in Debian 12 and Ubuntu 22.04 or later

```bash
sudo apt install libadwaita-1-dev libglib2.0-dev python-gi-dev gettext #Runtime Dependencies
sudo apt install meson gobject-introspection #Build Dependencies
```

#### On Arch/Manjaro

```bash
sudo pacman -S libadwaita glib2 python-gobject gettext #Runtime Dependencies
sudo pacman -S meson gobject-introspection #Build Dependencies
```

## Contribute

- [Report Bugs](https://github.com/realmazharhussain/gdm-settings/issues/new?assignees=&labels=bug&template=bug_report.yml&title=%5BBUG%5D+)
- [Translate](docs/translate.md)
- [Donate](https://www.patreon.com/mazharhussain)
