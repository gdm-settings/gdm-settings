#!/bin/bash

set -e

export ProjectName=gdm-settings
export ApplicationId=io.github.realmazharhussain.GdmSettings


export ScriptDir=$(realpath "$0" | xargs dirname)

SourceDir=${ScriptDir}
while true; do
  if test -z "${SourceDir}"; then
    echo "Could not find root directory of the source code" >&2; exit 1
  elif test -f "${SourceDir}"/LICENSE; then
    break
  else
    SourceDir=${SourceDir%/*}
  fi
done

export SourceDir
export BuildDir=${SourceDir}/build
export AppDir=${BuildDir}/AppDir
export AppRun="${AppDir}"/AppRun


cleanup() {
  rm -rf "${AppDir}"
}
trap cleanup EXIT


source "${ScriptDir}"/utils.sh


mkdir -p "${AppDir}"

echo '#!/usr/bin/env bash' > "${AppRun}"
cat "${ScriptDir}"/default_vars >> "${AppRun}"

source "${ScriptDir}"/deps/GLibC.sh
source "${ScriptDir}"/deps/Adw.sh
source "${ScriptDir}"/deps/GIR.sh
source "${ScriptDir}"/deps/Python.sh

echo 'gdm-settings "$@"' >> "${AppRun}"
chmod 755 "${AppRun}"

echo


if test -f "${BuildDir}/build.ninja"; then
  reconfigure="--reconfigure"
fi

meson "${BuildDir}" --prefix=/usr ${reconfigure}
meson compile -C "${BuildDir}"
meson install -C "${BuildDir}" --destdir=AppDir


glib-compile-schemas "${AppDir}"/usr/share/glib-2.0/schemas
gtk4-update-icon-cache -q -t -f "${AppDir}"/usr/share/icons/hicolor
ln -sfr "${AppDir}"/usr/share/applications/${ApplicationId}.desktop "${AppDir}"/
if which magick &>/dev/null; then
  magick -background none "${AppDir}"/usr/share/icons/hicolor/scalable/apps/${ApplicationId}.svg "${AppDir}"/${ApplicationId}.png
else
  ln -sfr "${AppDir}"/usr/share/icons/hicolor/scalable/apps/${ApplicationId}.svg "${AppDir}"/
fi

echo


VERSION_STRING=$("${AppDir}"/usr/bin/gdm-settings --version)
export VERSION=${VERSION_STRING##* }
appimagetool "${AppDir}" "${BuildDir}"/${ProjectName}.AppImage
