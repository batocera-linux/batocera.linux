#!/bin/sh

ACTION=$1

export DISPLAY=:0.0
RESOLUTION=$(batocera-resolution currentResolution)
OUTPUT="/userdata/screenshots/capture-$(date +%Y.%m.%d-%Hh%M.%S).mkv"
mkdir -p /userdata/screenshots || exit 1

usage() {
    echo "${1} --default"     >&2
    echo "${1} --fast"        >&2
    echo "${1} --compress"    >&2
}

default_record(){
ffmpeg -video_size "${RESOLUTION}" -framerate 25 -f x11grab -i :0.0+0,0 "${OUTPUT}"
}

fast_record(){
ffmpeg -video_size "${RESOLUTION}" -framerate 30 -f x11grab -i :0.0 -c:v libx264rgb -crf 0 -preset ultrafast "${OUTPUT}"
}

compress_record(){
ffmpeg -video_size "${RESOLUTION}" -framerate 30 -f x11grab -i :0.0 -c:v libx264rgb -crf 20 -preset veryfast "${OUTPUT}"
}


case "${ACTION}" in
        --fast)
        fast_record || exit 1
        ;;
        --default)
        default_record || exit 1
        ;;
        --compress)
        compress_record || exit 1
        ;;
        -h|--help)
        usage "${0}" || exit 1
        exit 0
        ;;
        *)
        default_record || exit 1
        ;;
esac
