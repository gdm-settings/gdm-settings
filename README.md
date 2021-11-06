# gdm-settings

An app to change settings of Gnome's Display/Login Manager.

It is written in Python and provides a Graphical interface using GTK+ library. It is an alternative to '[gdm-tools](https://github.com/realmazharhussain/gdm-tools.git)'  which is written in bash and has no Graphical Interface.

<center><img src="resources/screenshot.png" alt="screenshot"/></center>

## Important Note! (Alpha-Stage Software)

This app is in very early stage of development. So, it has only a small number of features and may crash frequently. Also, every aspect of this app is subject to significant change.

## What works perfectly?

Nothing

## What works with "problems"?

**Note:** The problems are planned to be resolved in future versions

- ### Apply Themes

  The app can apply themes to GDM. But, only third-party themes can be applied and the default GDM theme gets replaced by the theme you apply. As a result, the default theme is gone after you apply a theme using this app.

  #### Solutions:

  - Re-install 'gnome-shell-common' package (or 'gnome-shell' package if 'gnome-shell-common' is not available) to restore the default theme.
  - Use '[gdm-tools](https://github.com/realmazharhussain/gdm-tools.git)' to create and restore backup of the default theme
  - Manually backup `/usr/share/gnome-shell/gnome-shell-theme.gresource` before applying a theme

## How to Install?

Currently there is no way to install this app. Just clone the git repository and double-click on the file 'gdm-settings' to run the app or manually integrate it with the system by using the desktop file.

## Issues to be resolved

- No easy method to install the app
- No icon for the app

## Planned Features

- Save/Backup default theme before applying third-party themes
- Apply default theme
- Change background image/color
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
- Add user-specified CSS to  the theme before applying it
- A command-line interface
- Tab-completion for the command-line interface

