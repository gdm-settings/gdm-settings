#!/bin/bash -e
repo_dir=$(dirname "$(realpath "$0")")
build_dir=${repo_dir}/build
app_dir=${build_dir}/AppDir

rm -rf "${app_dir}"

action=setup
if test -d "${build_dir}"; then
  action=configure
fi

meson $action build --prefix="${app_dir}"/usr
meson install -C build

export LD_LIBRARY_PATH="${app_dir}/usr/lib"
export GI_TYPELIB_PATH="${app_dir}/usr/lib/girepository-1.0"
"${app_dir}"/usr/bin/gdm-settings "$@"