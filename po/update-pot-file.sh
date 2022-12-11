#!/bin/bash
po_dir=$(dirname "$(realpath "$0")")

options=(
  -f "$po_dir"/POTFILES.in
  -o "$po_dir"/gdm-settings.pot
  --add-comments=Translators
  --keyword=_
  --keyword=C_:1c,2
  --from-code=UTF-8

  --package-name="gdm-settings"
  --package-version="3.alpha"
  --msgid-bugs-address="realmazharhussain@gmail.com"
)

output=$(xgettext "${options[@]}" 2>&1)
status=$?

while read line
do
  if [[ "$line" != *"extension 'blp' is unknown; will try C" ]]; then
    echo "$line" >&2
  fi
done <<< "$output"

exit $status
