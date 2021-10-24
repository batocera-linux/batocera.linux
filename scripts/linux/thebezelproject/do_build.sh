#!/bin/bash

mkdir -p logs || exit 1
./tbp-md5gen generate all || exit 1
cp ./resources/default.{png,info} ./thebezelproject || exit 1
echo success
exit 0

