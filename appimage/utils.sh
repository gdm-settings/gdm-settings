# Detect multiarch directory
if [ -d /usr/lib/x86_64-linux-gnu ]; then
  # Ubuntu x64
  export LIBDIR=/usr/lib/x86_64-linux-gnu
else
  # Standard path
  export LIBDIR=/usr/lib
fi

copy() {
  for elem in "$@"; do
    mkdir --parents "${AppDir}/$(dirname "${elem}")"
    cp "${elem}" --archive --parents --target-directory="${AppDir}"
  done
}

# Try to copy from multiple possible paths, using the first one that exists
# Usage: try_copy "path1" "path2" "path3" ...
# Exits with error if none of the paths exist
try_copy() {
  local paths=("$@")
  local found=false

  # Try each path in order
  for path in "${paths[@]}"; do
    if compgen -G "$path" > /dev/null 2>&1; then
      copy "$path" 2>/dev/null || true
      found=true
      break
    fi
  done

  # If no path was found, print error and exit
  if [ "$found" = false ]; then
    echo "Error: Could not find files in any of the following locations:"
    for path in "${paths[@]}"; do
      echo "  - $path"
    done
    exit 1
  fi
}

# Try to copy from multiple possible paths, using the first one that exists
# Usage: try_copy_optional "path1" "path2" "path3" ...
# Only warns if none of the paths exist (does not exit)
try_copy_optional() {
  local paths=("$@")
  local found=false

  # Try each path in order
  for path in "${paths[@]}"; do
    if compgen -G "$path" > /dev/null 2>&1; then
      copy "$path" 2>/dev/null || true
      found=true
      break
    fi
  done

  # If no path was found, print warning but continue
  if [ "$found" = false ]; then
    echo "Warning: Could not find files in any of the following locations:"
    for path in "${paths[@]}"; do
      echo "  - $path"
    done
    echo "This is optional and the build will continue."
  fi
}
