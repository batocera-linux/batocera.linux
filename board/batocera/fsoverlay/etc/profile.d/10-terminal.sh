# Set vt100 as terminal enviroment if none is set per SSH client
if test -z $TERM; then
    TERM=vt100
fi
