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

    # Set $@ to run the docker command as the "batocera" user and group.
    # NOTE: gosu (like su) resolves HOME/USER/LOGNAME from the target UID's
    # /etc/passwd entry itself, overriding the HOME exported above. Ubuntu's
    # official images (24.04/noble onward) ship a built-in "ubuntu" account
    # already allocated at UID 1000 -- the same UID most single-user Linux
    # hosts assign their first regular user. useradd -o above only adds a
    # second passwd entry for that UID rather than replacing the existing
    # one, so gosu's uid->passwd lookup can resolve to "ubuntu" instead of
    # "batocera", silently resetting HOME to /home/ubuntu, a path nothing
    # here mounts -- breaking anything HOME-relative (e.g. ccache's default
    # cache dir) with no visible error. Re-asserting HOME explicitly after
    # gosu sidesteps the lookup instead of depending on it.
    set -- gosu "$HOST_UID":"$HOST_GID" env HOME=/home/batocera "$@"
fi

exec "$@"
