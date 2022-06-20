#!/bin/bash
po_dir=$(dirname "$(realpath "$0")")

options=(
  -f "$po_dir"/POTFILES.in
  -o "$po_dir"/gdm-settings.pot
  --add-comments=Translators
  --keyword=_
  --keyword=C_:1c,2
  --from-code=UTF-8
)

xgettext "${options[@]}" 2>/dev/null
