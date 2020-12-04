#!/bin/sh

# use to hide password from people having no access to the ssh connection
# based on unique values of you rpi :
#    * based on the mac address of the ethernet card (so, not for rpi0) - not secure for people having access to the local network, but for people having access to your external drive or batocera.conf file
#    * based on the rpi serial number - limited security while it's only 8 numbers and guessable partially i think

ACTION=$1
CODE=$2

getPassword() {
    SERIAL=$(grep -E '^Serial' /proc/cpuinfo | sed -e s+'^Serial[\t]*: '++)
    ETHMAC=$(cat /sys/class/net/eth*/address)
    echo "${SERIAL}${ETHMAC}"
}

case "${ACTION}" in
    "decode")
	if echo "${CODE}" | grep -qE '^enc:'
	then
	    PASSWORD=$(getPassword)
	    if ! echo "${CODE}" | sed -e s+"^enc:"++ | openssl enc -aes-128-cbc -a -d -salt -pass pass:"${PASSWORD}"
	    then
		exit 1
	    fi
	else
	    echo "${CODE}"
	fi
    ;;

    "encode")
	PASSWORD=$(getPassword)
	CODE=$(echo "${CODE}" | openssl enc -aes-128-cbc -a -salt -pass pass:"${PASSWORD}")
	echo "enc:${CODE}"
    ;;
esac

exit 0
