#!/bin/bash
progName=$(basename "$0")
progDir=$(realpath "$0" | xargs dirname)
PREFIX=${PREFIX:-/usr/local}
DESTDIR=${DESTDIR:-}

eval $("$progDir"/load_info.sh)
source "$progDir"/colors.sh

HelpText="${bold}A script to uninstall '$application_name' app${normal}

${bold}Usage:${normal} $0 [Options]

${bold}Options:${normal}
    -h,--help      Print this help message
    --destdir      Destination root directory
    --prefix       Prefix directory (e.g. /usr or /usr/local)

${bold}Note:${normal} This script also supports DESTDIR and PREFIX environment variables"

# Start Option Parsing
TEMP=$(getopt -l 'help,destdir:,prefix:' -o 'h' -n "$0" -- "$@")
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
      --)
         shift
         break
   esac
done
if test $# -gt 0; then
   {
      echo -n "$0: unknown arguments"
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
   [ -n "$1" ] && [ -d "$1" ] && [ -w "$1" ] && return 1
   return 0
}

if requires_sudo "$DESTDIR" || requires_sudo "${targetDir}"; then
   SUDO=sudo
fi

source "$progDir"/filemaps

print_message() {
   echo "  $1"
}

echo "${bold}Removing files ...${normal}"
for filemap in "${files[@]}"; do
   target=${filemap#*:}
   target_full=${targetDir}/${target}
   target_nice=${DESTDIR}${PREFIX}/${target}
   sources_string=${filemap%:*}
   eval sources_list=("'$progDir'/$sources_string")
   for source_full in "${sources_list[@]}"; do
      source_basename=$(basename "$source_full")
      if $SUDO rm -f "${target_full}/${source_basename}"; then
         print_message "${target_nice}/${source_basename}"
      fi
   done
   if $SUDO rmdir "$target_full" &>/dev/null; then
      print_message "$target_nice"
   fi
done
for dirmap in "${dirs[@]}"; do
   target=${dirmap#*:}
   target_full=${targetDir}/${target}
   target_nice=${DESTDIR}${PREFIX}/${target}
   source_nice=${dirmap%:*}
   source_full=${progDir}/${source_nice}
   find "$source_full" -type f,l |  while read line; do
      source_file=${line#"$source_full/"}
      if $SUDO rm -f "${target_nice}/${source_file}"; then
         print_message "${target_nice}/${source_file}"
      fi
   done
done
for linkmap in "${links[@]}"; do
   source=${linkmap%:*}
   target=${linkmap#*:}
   source_full=${targetDir}/${source}
   target_full=${targetDir}/${target}
   source_nice=${DESTDIR}${PREFIX}/${source}
   target_nice=${DESTDIR}${PREFIX}/${target}
   if $SUDO rm -f "$target_full"; then
      print_message "$target_nice"
   fi
done
