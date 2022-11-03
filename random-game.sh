#!/bin/sh
set -ue

HISTORY_FILE="$HOME/.random-game-history"

selected=$(find "$HOME/.steam/steam/steamapps" \
	-name 'appmanifest_*.acf' \
	$(sed 's/^/-and -not -name appmanifest_/;s/$/.acf/' < "$HISTORY_FILE" 2>/dev/null) \
	| shuf -n1 \
	| sed 's/.*appmanifest_//;s/\.acf//')

if [ -z "$selected" ]; then
	echo "ERROR: couldn't make a selection, do you have any Steam games installed?" 1>&2
	exit 1
fi

echo "$selected" >> "$HISTORY_FILE"
steam "steam://nav/games/details/$selected"
