#!/bin/bash

echo -e "\nUPDATE LOG - `date`\n" >> /root/updates.log

source /recalbox/scripts/rsync-update/rsync-password.sh
echo "begin update" > /root/updates.log

if (($? != 0)); then
	echo "error : UNABLE TO GET PASSWORD FROM /recalbox/scripts/rsync-update/rsync-password.sh" >> /root/updates.log
	exit 90
fi

echo "info : will conntect to ${RSYNC_SERVER} with credential : ${RSYNC_USER}" >> /root/updates.log
echo "info : starting share update" >> /root/updates.log

rsync -rltXv --exclude-from=/recalbox/scripts/rsync-update/always-exclude.cfg --exclude-from=/recalbox/scripts/rsync-update/exclude-share.cfg rsync://${RSYNC_USER}@${RSYNC_SERVER}/recalbox-share /recalbox/share >> /root/updates.log
if (($? != 0)); then
        echo "error : unable to update share" >> /root/updates.log
        exit 91
fi
echo "info : starting boot update" >> /root/updates.log
rsync -rltXv --exclude-from=/recalbox/scripts/rsync-update/always-exclude.cfg --exclude-from=/recalbox/scripts/rsync-update/exclude-boot.cfg rsync://${RSYNC_USER}@${RSYNC_SERVER}/recalbox-boot /boot >> /root/updates.log
if (($? != 0)); then
        echo "error : unable to update boot" >> /root/updates.log
        exit 91
fi
echo "info : starting root update" >> /root/updates.log
rsync -aXv --exclude-from=/recalbox/scripts/rsync-update/always-exclude.cfg --exclude-from=/recalbox/scripts/rsync-update/exclude-root.cfg rsync://${RSYNC_USER}@${RSYNC_SERVER}/recalbox-root / >> /root/updates.log
if (($? != 0)); then
        echo "error : unable to update root" >> /root/updates.log
        exit 91
fi

# POST UPDATE
/recalbox/scripts/rsync-update/updates/00-post-update-script.sh >> /root/updates.log
error="$?"
if (("$error" != "0")); then
        echo "error : post update error" >> /root/updates.log
        exit "$error"
fi

echo "info : UPDATE OK" >> /root/updates.log
