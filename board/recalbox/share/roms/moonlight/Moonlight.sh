#!/bin/bash

cd /recalbox/share/roms/moonlight/
moonlight_dir=$PWD
moonlight_mapping="$moonlight_dir/mapping.conf"
moonlight_conf="/recalbox/share/system/moonlight.conf"

case $1 in
    map)
        cmd="moonlight map ${moonlight_mapping}" ;;

    pair)
        cmd="moonlight pair -config ${moonlight_conf}" ;;

    *)
        cmd="moonlight stream -config ${moonlight_conf} -mapping ${moonlight_mapping}" ;;

esac

exec $cmd