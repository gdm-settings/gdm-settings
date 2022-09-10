copy() {
  for elem in "$@"; do
    mkdir --parents "${AppDir}/$(dirname "${elem}")"
    cp "${elem}" --archive --parents --target-directory="${AppDir}"
  done
}

copy_bin() {
  for elem in "$@"; do
    cp --archive --no-target-directory /usr/bin/"${elem}" "${AppDir}"/usr/bin/"${elem}".bin

    echo "#!/bin/sh" > "${AppDir}"/usr/bin/"${elem}"

    cmd=(exec '"${AppDir}"/usr/lib/ld-linux-x86-64.so.2'
         --library-path '"${AppDir}"/usr/lib'
         '"${AppDir}"'/usr/bin/${elem}.bin '"$@"'
         )
    echo "${cmd[*]}" >> "${AppDir}"/usr/bin/"${elem}"

    chmod 755 "${AppDir}"/usr/bin/"${elem}"
  done
}
