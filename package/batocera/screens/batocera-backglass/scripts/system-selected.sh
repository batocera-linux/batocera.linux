#!/bin/sh

GSYSTEM=$1

echo "${GSYSTEM}" > /tmp/es_active_system.txt

txt2http() {
    jq -sRr @uri
}

GSYSTEM=$(echo -n "${GSYSTEM}" | txt2http)
curl "http://localhost:2033/system?system=${GSYSTEM}"
