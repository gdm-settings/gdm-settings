#!/bin/bash -e
repo_dir=$(dirname "$(realpath "$0")")
temp_dir=$(mktemp -d)
app_dir=${temp_dir}/app
build_dir=${temp_dir}/build

cleanup() {
  rm -rf "${temp_dir}"
}
trap cleanup EXIT


TEMP=$(getopt -l 'command:,help' -o 'c:h' -- "$@")
eval set -- "$TEMP"
unset TEMP

command=${SHELL:-/usr/bin/bash}
help="Usage: $0 [OPTIONS] -- [ARGUMENT ...]

Options:
  -h,--help               Print this help message
  -c,--command COMMAND    Run COMMAND instead of \$SHELL ($command)

ARGUMENTs are passed to the COMMAND as is."

while true; do
  case "$1" in
    -h | --help)
      echo "$help" && exit 0
    ;;
    -c | --command)
      command=$2
      shift 2
      continue
    ;;
    --)
      shift
      break
    ;;
  esac
done


meson setup "${build_dir}" --prefix=/app
meson install -C "${build_dir}" --destdir="${temp_dir}"

glib-compile-schemas "${app_dir}"/share/glib-2.0/schemas
gtk4-update-icon-cache -t -f "${app_dir}"/share/icons/hicolor


export PATH="${app_dir}/bin:${PATH}"
export XDG_DATA_DIRS="${app_dir}/share:${XDG_DATA_DIRS:-/usr/local/share:/usr/share}"
export TEXTDOMAINDIR="${app_dir}"/share/locale
export LD_LIBRARY_PATH="${app_dir}"/lib
export GI_TYPELIB_PATH="${app_dir}"/lib/girepository-1.0

_postfix=$(python3 --version | cut -d' ' -f2 | cut -d. -f1,2)
export PYTHONPATH="${app_dir}"/lib/python${_postfix}/site-packages


cd "${app_dir}"
"$command" "$@"
exit $?
