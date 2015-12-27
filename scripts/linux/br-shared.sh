#!/bin/bash -e

export arch="${1}"

if [ -z "${arch}" ]; then
    export arch="rpi1"
fi

export br_pwd="${PWD}"
export br_build_pwd="${br_pwd}/../builds/br-${arch}"
