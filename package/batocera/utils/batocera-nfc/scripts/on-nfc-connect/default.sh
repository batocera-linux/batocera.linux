#!/bin/sh

TAG=$1

# start the game only if none is already running
CURRENT=$(curl -s http://127.0.0.1:1234/runningGame | jq -r '.name')
if test "${CURRENT}" = null
then
	curl -s -X POST http://127.0.0.1:1234/launch -d "${TAG}"
fi
