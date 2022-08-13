#!/bin/bash
progDir=$(realpath "$0" | xargs dirname)
buildDir="$progDir"/build
AppDir="$buildDir"/AppDir
export ARCH=x86_64
export DESTDIR=${AppDir#"$PWD/"}
export PREFIX=/usr

ProjectName=gdm-settings
ApplicationId=io.github.realmazharhussain.GdmSettings

# Text styles and colors
normal=$'\e[0m'
bold=$'\e[1m'
italic=$'\e[3m'
red=$'\e[31m'
light_bg=$'\e[47m'

if test -d "$buildDir"; then
  meson "$buildDir" --prefix=$PREFIX --reconfigure
else
  meson "$buildDir" --prefix=$PREFIX
fi
meson compile -C "$buildDir"
meson install -C "$buildDir" --destdir="$(realpath "$DESTDIR")"

#eval $("$progDir"/load_info.py "$buildDir"/src/info.py)

AppRun='#!/usr/bin/bash
#progDir=$(dirname "$(realpath "$0")")
progDir=$APPDIR
export XDG_DATA_DIRS="${progDir}/usr/share:${XDG_DATA_DIRS:-/usr/local/share:/usr/share}"
export PATH="${progDir}/usr/bin:${PATH}"
export TEXTDOMAINDIR="${progDir}"/usr/share/locale:"$TEXTDOMAINDIR"
export LD_LIBRARY_PATH="${progDir}"/usr/lib:${LD_LIBRARY_PATH:-/usr/local/lib:/usr/lib}
gdm-settings "$@"'

echo "${bold}${italic}Installing to a temporary AppDir ...${normal}"
glib-compile-schemas "$AppDir"/usr/share/glib-2.0/schemas
rm -rf "$AppDir"/usr/share/metainfo
ln -sfr "$AppDir"/usr/share/applications/$ApplicationId.desktop "$AppDir"/
if which magick &>/dev/null; then
  magick -background none "$AppDir"/usr/share/icons/hicolor/scalable/apps/$ApplicationId.svg "$AppDir"/$ApplicationId.png
else
  ln -sfr "$AppDir"/usr/share/icons/hicolor/scalable/apps/$ApplicationId.svg "$AppDir"/
fi
echo "$AppRun" > "${AppDir}/AppRun"
chmod +x "${AppDir}/AppRun"
echo '  Done.'

echo "${bold}${italic}Building AppImage ...${normal}"
if output=$(appimagetool "$AppDir" "$buildDir/$ProjectName.AppImage" 2>&1); then
   echo "  Success! AppImage saved as '${buildDir/$PWD/.}/$ProjectName.AppImage'"
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
