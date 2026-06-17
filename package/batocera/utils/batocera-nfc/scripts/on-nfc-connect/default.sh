#!/bin/sh

TAG=$1

# check for emulationstation.ready-file: https://stackoverflow.com/questions/70132359
# watch dir tmp for creation of any file --include means only emulationstation.ready - regex-include always searches for full path so /file.name$ is valid
! [ -e /tmp/emulationstation.ready ] && inotifywait -t 60 -e create --include '/emulationstation\.ready$' /tmp

# start the game only if none is already running
CURRENT=$(curl -s http://127.0.0.1:1234/runningGame | jq -r '.name')
if test "${CURRENT}" = null
then
	curl -s -X POST http://127.0.0.1:1234/launch -d "${TAG}"
fi
