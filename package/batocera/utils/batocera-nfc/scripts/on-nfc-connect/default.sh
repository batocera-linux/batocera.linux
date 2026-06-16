#!/bin/sh

TAG=$1

# wait for ES webserver to be ready (up to 60 seconds)
TRIES=0
while [ $TRIES -lt 60 ]; do
    curl -s http://127.0.0.1:1234/runningGame > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        break
    fi
    sleep 1
    TRIES=$((TRIES + 1))
done


# start the game only if none is already running
CURRENT=$(curl -s http://127.0.0.1:1234/runningGame | jq -r '.name')
if test "${CURRENT}" = null
then
	curl -s -X POST http://127.0.0.1:1234/launch -d "${TAG}"
fi
