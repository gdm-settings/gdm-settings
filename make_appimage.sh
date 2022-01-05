#!/bin/bash
progDir=$(realpath "$0" | xargs dirname)
buildDir="$progDir"/build
AppDir="$buildDir"/AppDir
appID=org.gtk.GdmSettings
export ARCH=x86_64
export DESTDIR=${AppDir#"$PWD/"}
export PREFIX=/usr

source "$progDir"/colors.sh

AppRun='#!/usr/bin/bash
progDir=$(dirname "$(realpath "$0")")
export XDG_DATA_DIRS=${XDG_DATA_DIRS:-/usr/local/share:/usr/share}
export XDG_DATA_DIRS="${progDir}/usr/share:${XDG_DATA_DIRS}"
export PATH="${progDir}/usr/bin:${PATH}"
gdm-settings'

echo "${bold}${italic}Installing to a temporary AppDir ...${normal}"
"$progDir"/install.sh --relative | while IFS='' read line; do echo "  $line"; done
rm -rf "$AppDir"/usr/share/metainfo
ln -sfr "$AppDir"/usr/share/applications/$appID.desktop "$AppDir"/
ln -sfr "$AppDir"/usr/share/icons/hicolor/scalable/apps/$appID.svg "$AppDir"/
echo "$AppRun" > "${AppDir}/AppRun"
chmod +x "${AppDir}/AppRun"

echo "${bold}${italic}Building AppImage ...${normal}"
if output=$(appimagetool "$AppDir" "$buildDir/GDM Settings.AppImage" 2>&1); then
   echo "  Success!"
   status=0
else
   echo "  ${bold}${red}${light_bg}Failed!${normal}"
   status=1
   echo "${bold}${italic}Printing Build Log ...${normal}"
   while read line; do echo "  $line"; done <<< "$output"
fi
echo "${bold}${italic}Removing temporary AppDir ...${normal}"
rm -rf "$AppDir"
exit $status
