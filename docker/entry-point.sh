#!/bin/bash
set -e

if [ ! -z "$HOST_UID" ] && [ ! -z "$HOST_GID" ]; then
    # Create "batocera" user and group with the same UID and GID as the host user
    groupadd -o -g "$HOST_GID" batocera 2>/dev/null
    useradd -o -u "$HOST_UID" -g "$HOST_GID" -d /home/batocera -c '' -M -s /bin/bash batocera 2>/dev/null

    # This should already be made, but create it just in case
    mkdir -p /home/batocera

    # Set the ownership of the home directory to the "batocera" user and group
    # NOTE: this is not done recursively because the build process mounts the
    # ccache directory in /home/batocera/.ccache and we don't want to change
    # the ownership of all of those files (since they should already have the
    # correct ownership)
    chown batocera:batocera /home/batocera

    export HOME=/home/batocera

    # Set $@ to run the docker command as the "batocera" user and group
    set -- gosu "$HOST_UID":"$HOST_GID" "$@"
fi

exec "$@"
