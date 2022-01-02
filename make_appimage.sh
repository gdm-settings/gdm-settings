#!/bin/bash
progDir=$(realpath "$0" | xargs dirname)
buildDir="$progDir"/build
AppDir="$buildDir"/AppDir
export ARCH=x86_64
"$progDir"/install.sh --destdir="$AppDir" --prefix=/usr --relative
ln -sfr "$AppDir"/usr/bin/gdm-settings "$AppDir"/AppRun
ln -sfr "$AppDir"/usr/share/applications/gdm-settings.desktop "$AppDir"/
ln -sfr "$AppDir"/usr/share/icons/hicolor/scalable/apps/gdm-settings.svg "$AppDir"/
appimagetool "$AppDir" "$buildDir/GDM Settings.AppImage"
rm -rf "$AppDir"
