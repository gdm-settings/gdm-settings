# GDM Settings 

An app to change settings of Gnome's Display/Login Manager.

It is written in Python and provides a Graphical interface using GTK+ and LibAdwaita. It is an alternative to '[gdm-tools](https://github.com/realmazharhussain/gdm-tools)'  which is written in bash and has no Graphical Interface.

<center><img src="resources/screenshot.png" alt="screenshot"/></center>

## Important Note! (Alpha-Stage Software)

This app is in very early stage of development. So, it has only a small number of features and may crash frequently. Also, every aspect of this app is subject to significant change.

## What works in Graphical Interface?

- Apply themes

## What works in Command-line Interface?

- Apply themes
- Create/Restore a backup of the default theme
- Extract default theme for use in gnome-shell

## What works with some issues?

**Note:** These issues are planned to be resolved

- Change Background Image\
  **Issues:**
  - You need to manually put an image as the file `/usr/share/gnome-shell/theme/gdm-background` (Note: no extension)
- Apply Custom Styling to a Theme\
  **Issues:**
  - You need to manually create CSS file `/etc/gdm-settings/custom.css` and put your custom CSS code in there

## How to Install?

### Manual Installation

0. Make sure all build-time and run-time dependencies are installed

1. Download and extract [this zip file](https://github.com/realmazharhussain/gdm-settings/archive/refs/heads/main.zip)\
   OR\
   Clone this repository. You can do so with the command `git clone --depth=1 --singe-branch https://github.com/realmazharhussain/gdm-settings`
2. Go to the folder where you extracted/cloned this file/repo
3. Open your terminal application in that folder
4. Type `./install.sh` and press Enter
5. Type your password and press Enter

### Arch-based distros

This app is available in the AUR as [gdm-settings-git](https://aur.archlinux.org/packages/gdm-settings-git). You can install it using your favorite AUR helper.

## Dependencies

### Run-time Dependencies

- LibAdwaita-1
- Glib-2 (development version)
- python-gobject a.k.a PyGObject
- python-magic

### Build-time Dependencies

- Bash

## Planned Features

- Change background image/color (<font color="red">partially done</font>)
- Change icon theme
- Change cursor theme
- Night light settings
- Show/Hide battery percentage
- Touchpad settings (speed, tap-to-click)
- Clock settings (show/hide weekday, AM/PM or 24h)
- Tweak the theme before applying it. For example, 
  - make text white or black
  - disable arrows in top bar
  - make top bar partially/fully transparent
- Add user-specified CSS to  the theme before applying it (<font color="red">partially done</font>)
- A command-line interface (<font color="red">partially done</font>)
- Tab-completion for the command-line interface

