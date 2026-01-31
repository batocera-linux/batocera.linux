#!/bin/sh

TAG=$1

# stop the game only if one is already running
CURRENT=$(curl -s http://127.0.0.1:1234/runningGame | jq -r '.name')
if test "${CURRENT}" != null
then
  hotkeygen --send exit
fi

