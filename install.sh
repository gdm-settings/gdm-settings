#!/bin/bash
progName=$(basename "$0")
progDir=$(realpath "$0" | xargs dirname)
PREFIX=${PREFIX:-/usr/local}
DESTDIR=${DESTDIR:-}
appID=org.gtk.GdmSettings
use_relative_links=auto

source "$progDir"/colors.sh

HelpText="${bold}A script to install 'GDM Settings' app

Usage:${normal} $0 [Options]

${bold}Options:${normal}
    -h,--help      Print this help message
    -r,--relative  Use relative symlinks
                   Optional values: auto (default), yes, no
    --destdir      Destination root directory
    --prefix       Prefix directory (e.g. /usr or /usr/local)

${bold}Note:${normal} This script also supports DESTDIR and PREFIX environment variables"

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
                  echo "${bold}Acceptable values:${normal} auto, yes,true,1, no,false,0"
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

if test $use_relative_links = auto; then
   if test -n "$DESTDIR"; then
      use_relative_links=true
   else
      use_relative_links=false
   fi
fi

source "$progDir"/filemaps

print_message() {
   echo "   $1 $lime->$normal $2"
}

echo "${bold}Copying files ...${normal}"
for filemap in "${files[@]}"; do
   target=${filemap#*:}
   target_full=${targetDir}/${target}
   target_nice=${DESTDIR}${PREFIX}/${target}/
   sources_string=${filemap%:*}
   eval sources_list=("'$progDir'/$sources_string")
   $SUDO mkdir -p "$target_full"
   if $SUDO cp -f "${sources_list[@]}" "$target_full"/; then
      for source_full in "${sources_list[@]}"; do
         source_nice=${source_full#"$progDir/"}
         print_message "$source_nice" "$target_nice"
      done
   fi
done
for dirmap in "${dirs[@]}"; do
   target=${dirmap#*:}
   target_full=${targetDir}/${target}
   target_nice=${DESTDIR}${PREFIX}/${target}
   source_nice=${dirmap%:*}
   source_full=${progDir}/${source_nice}
   $SUDO mkdir -p "$target_full"
   if $SUDO cp -rfT "$source_full" "$target_full"/; then
      print_message "$source_nice" "$target_nice"
   fi
done
echo "${bold}Making symlinks ...${normal}"
pushd ${DESTDIR:-/} >/dev/null
for linkmap in "${links[@]}"; do
   source=${linkmap%:*}
   target=${linkmap#*:}
   source_full=${targetDir}/${source}
   target_full=${targetDir}/${target}
   source_nice=${DESTDIR}${PREFIX}/${source}
   target_nice=${DESTDIR}${PREFIX}/${target}
   $SUDO mkdir -p "$(dirname "$target_full")"
   if test $use_relative_links = true; then
      command="ln -srfT '$source_full' '$target_full'"
   else
      command="ln -sfT '${PREFIX}/${source}' '$target_full'"
   fi
   if eval $SUDO $command; then
      print_message "$source_nice" "$target_nice"
   fi
done
popd >/dev/null
