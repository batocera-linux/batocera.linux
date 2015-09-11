#!/bin/bash

cd /recalbox/share/roms/moonlight/
moonlight_dir=$PWD
moonlight_mapping="$moonlight_dir/mapping.conf"
moonlight_conf="$moonlight_dir/moonlight.conf"

case $1 in
    map)
        cmd="moonlight map ${moonlight_mapping}" ;;

    pair)
        cmd="moonlight pair -config ${moonlight_conf}" ;;

    *)
        cmd="moonlight stream -mapping ${moonlight_mapping} -config ${moonlight_conf}" ;;

esac

exec $cmd