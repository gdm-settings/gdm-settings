#!/bin/bash
progName=$(basename "$0")
progDir=$(realpath "$0" | xargs dirname)
PREFIX=${PREFIX:-/usr/local}
DESTDIR=${DESTDIR:-}
use_relative_links=auto

HelpText="A script to install 'GDM Settings' app

Usage: $0 [Options]

Options:
    -h,--help      Print this help message
    -r,--relative  Use relative symlinks
                   Optional values: auto (default), yes, no
    --destdir      Destination root directory
    --prefix       Prefix directory (e.g. /usr or /usr/local)

Note: This script also supports DESTDIR and PREFIX environment variables"

# Start Option Parsing
TEMP=$(getopt -l 'help,destdir:,prefix:,relative::' -o 'h,r::' -n "$0" -- "$@")
status=$?
test $status -ne 0 && exit $status
eval set -- "$TEMP"
while true; do
   case "$1" in
      --help|-h)
         echo "$HelpText"
         exit 0
         ;;
      --prefix)
         PREFIX=$2
         shift 2
         ;;
      --destdir)
         DESTDIR=$2
         shift 2
         ;;
      --relative|-r)
         case $2 in
            auto)
               use_relative_links=auto
               ;;
            0|no|false)
               use_relative_links=false
               ;;
            1|yes|true|'')
               use_relative_links=true
               ;;
            *)
               {
                  echo "$0: -r,--relative option does not accept value '$2'"
                  echo "Acceptable values: auto, yes,true,1, no,false,0"
               } >&2
               exit 3
               ;;
         esac
         shift 2
         ;;
      --)
         shift
         break
   esac
done
if test $# -gt 0; then
   {
      echo -n "$progName: unknown arguments"
      for arg in "$@"; do
         echo -n " '$arg'"
      done
      echo
   } >&2
   exit 2
fi
# End Option Parsing

targetDir=$(realpath -m "${DESTDIR}${PREFIX}")

requires_sudo() {
   if test -n "$1"; then
      if [ -d "$1" ]; then
         [ -w "$1" ] && return 1
      else
         mkdir -p "$1" 2>/dev/null && return 1
      fi
   fi
}
if requires_sudo "$DESTDIR" || requires_sudo "${targetDir}"; then
   SUDO=sudo
fi

link_option=''
case $use_relative_links in
   auto)
      test -n "$DESTDIR" && link_option='-r'
      ;;
   true)
      link_option='-r'
      ;;
esac

$SUDO mkdir -p "$targetDir"/{bin,share/{applications,gdm-settings}}
$SUDO cp "$progDir"/src/*.{ui,py} "$targetDir"/share/gdm-settings/
$SUDO cp "$progDir"/resources/*.desktop "$targetDir"/share/applications/
$SUDO ln -sf $link_option "$targetDir"/share/gdm-settings/gdm-settings.py "$targetDir"/bin/gdm-settings
$SUDO ln -sf $link_option "$targetDir"/share/gdm-settings/gdm-settings-cli.py "$targetDir"/bin/gdm-settings-cli

# Build and install app icon
hicolorDir="$targetDir"/share/icons/hicolor
iconSource="$progDir"/resources/gdm-settings.svg
for size in 16 24 32 48 64 96 128; do
   iconDir="$hicolorDir"/${size}x${size}/apps
   $SUDO mkdir -p "$iconDir"
   $SUDO magick -background none "$iconSource" -resize $size "$iconDir"/gdm-settings.png
done
iconDir="$hicolorDir"/scalable/apps
$SUDO mkdir -p "$iconDir"
$SUDO cp -t "$iconDir" "$iconSource"
