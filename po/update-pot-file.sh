#!/bin/sh
progDir=$(dirname "$(realpath "$0")")
pot_file="$progDir"/gdm-settings.pot
cd "$progDir"/..
POTFILES=(data{,/gschemas}/application_id.* src/*.py*)
BLPFILES=(src/blueprints/*.blp*)
rm -f "$pot_file"
xgettext -o "$pot_file" "${POTFILES[@]}"
xgettext -j -L Python -o "$pot_file" "${BLPFILES[@]}"
