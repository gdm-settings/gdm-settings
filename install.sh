#!/bin/bash
progName=$(basename "$0")
progDir=$(realpath "$0" | xargs dirname)
PREFIX=${PREFIX:-/usr/local}
DESTDIR=${DESTDIR:-}
relative_links=auto

# Start Option Parsing
TEMP=$(getopt -l 'destdir:,prefix:,relative::' -o 'r::' -n "$progName" -- "$@")
status=$?
test $status -ne 0 && exit $status
eval set -- "$TEMP"
while true; do
   case "$1" in
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
               relative_links=auto
               ;;
            0|no|false)
               relative_links=false
               ;;
            1|yes|true|'')
               relative_links=true
               ;;
            *)
               {
                  echo "$progName: -r,--relative option does not accept value '$2'"
                  echo "           it only accepts boolean values (yes,no,true,false,0,1) and 'auto'"
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

targetDir=$(realpath "${DESTDIR}${PREFIX}")

requires_sudo() {
   if test -n "$1"; then
      if [ -d "$1" ]; then
         [ -w "$1" ] && return 1
      else
         mkdir -p "$1" 2>/dev/null && return 1
      fi
   fi
}
if requires_sudo "$DESTDIR" || requires_sudo "${DESTDIR}${PREFIX}"; then
   SUDO=sudo
fi

link_option=''
case $relative_links in
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
