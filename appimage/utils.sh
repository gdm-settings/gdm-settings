copy() {
  for elem in "$@"; do
    mkdir --parents "${AppDir}/$(dirname "${elem}")"
    cp "${elem}" --archive --parents --target-directory="${AppDir}"
  done
}
