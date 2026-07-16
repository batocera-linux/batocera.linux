export XAUTHORITY=/var/lib/.Xauthority
d="$(getLocalXDisplay)"
[ -n "$d" ] && export DISPLAY="$d"
