#!/bin/bash
progDir=$(realpath "$0" | xargs dirname)
buildDir="$progDir"/build
AppDir="$buildDir"/AppDir
export ARCH=x86_64
export DESTDIR=${AppDir#"$PWD/"}
export PREFIX=/usr
export USE_RELATIVE_SYMLINKS=true

rm -rf "$buildDir"
meson "$buildDir" --prefix=$PREFIX
meson install -C "$buildDir" --destdir="$(realpath "$DESTDIR")"

eval $("$progDir"/load_info.sh "$buildDir/src/info.py")
source "$progDir"/colors.sh

AppRun='#!/usr/bin/bash
progDir=$(dirname "$(realpath "$0")")
export XDG_DATA_DIRS="${progDir}/usr/share:${XDG_DATA_DIRS:-/usr/local/share:/usr/share}"
export PATH="${progDir}/usr/bin:${PATH}"
'"$project_name"

echo "${bold}${italic}Installing to a temporary AppDir ...${normal}"
glib-compile-schemas "$AppDir"/usr/share/glib-2.0/schemas
rm -rf "$AppDir"/usr/share/metainfo
ln -sfr "$AppDir"/usr/share/applications/$application_id.desktop "$AppDir"/
ln -sfr "$AppDir"/usr/share/icons/hicolor/scalable/apps/$application_id.svg "$AppDir"/
echo "$AppRun" > "${AppDir}/AppRun"
chmod +x "${AppDir}/AppRun"
echo '  Done.'

echo "${bold}${italic}Building AppImage ...${normal}"
if output=$(appimagetool "$AppDir" "$buildDir/$project_name.AppImage" 2>&1); then
   echo "  Success! AppImage saved as '${buildDir/$PWD/.}/$project_name.AppImage'"
   status=0
else
   echo "  ${bold}${red}${light_bg}Failed!${normal}"
   status=1
   echo "${bold}${italic}Printing Build Log ...${normal}"
   while read line; do echo "  $line"; done <<< "$output"
fi
echo "${bold}${italic}Removing temporary AppDir ...${normal}"
rm -rf "$AppDir" && echo '  Done.'
exit $status
