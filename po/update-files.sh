#!/bin/bash
progDir=$(dirname "$(realpath "$0")")
cd "$progDir"/..

pot_file=po/gdm-settings.pot
POTFILES=(data{,/gschemas}/application_id.* src/*.py*)
BLPFILES=(src/blueprints/*.blp*)

echo "Updating '$pot_file' ..."
rm -f "$pot_file"
xgettext --add-comments=Translators -o "$pot_file" "${POTFILES[@]}"
xgettext --add-comments=Translators -j -L ObjectiveC --from-code=UTF-8 -o "$pot_file" "${BLPFILES[@]}"

for po_file in po/*.po
do
  echo "Updating '$po_file' ..."
  msgmerge -U --backup=off "$po_file" "$pot_file" 2>/dev/null
done
