#!/bin/bash

ROM=$1

unclutter-remote -s

GAMEDIR=$(dirname "${ROM}")

cd "${GAMEDIR}" && pygame "${ROM}"
EXITCODE=$?

unclutter-remote -h

exit "${EXITCODE}"
