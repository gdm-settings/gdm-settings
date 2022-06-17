#!/bin/bash
progDir=$(dirname "$(realpath "$0")")
pot_file="$progDir"/gdm-settings.pot
cd "$progDir"/..
POTFILES=(data{,/gschemas}/application_id.* src/*.py*)
BLPFILES=(src/blueprints/*.blp*)
rm -f "$pot_file"
xgettext --add-comments=Translators -o "$pot_file" "${POTFILES[@]}"
xgettext --add-comments=Translators -j -L ObjectiveC --from-code=UTF-8 -o "$pot_file" "${BLPFILES[@]}"
