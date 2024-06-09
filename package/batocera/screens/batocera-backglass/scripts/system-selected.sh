#!/bin/sh

GSYSTEM=$1

txt2http() {
    jq -sRr @uri
}

GSYSTEM=$(echo -n "${GSYSTEM}" | txt2http)
curl "http://localhost:2033/system?system=${GSYSTEM}"
