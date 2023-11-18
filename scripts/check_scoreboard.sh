#!/bin/bash
## NOTICE
# Dirty quick script to track the Cybertalent 2023 scoreboard. Buy me a beer :))

## CONSTANTS
SCRIPT_PATH="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

## GOGO
echo "Starting script..."
cd $SCRIPT_PATH # dirty

python3 "$SCRIPT_PATH/check_scoreboard.py"

if [[ `git status --porcelain` ]]; then
	echo "There are differences, updating"
  python3 "$SCRIPT_PATH/generate_html.py"
	git add -A
	git commit -m "[SCOREBOARD] Update"
	git push origin main
else
	echo "No differences"
fi
