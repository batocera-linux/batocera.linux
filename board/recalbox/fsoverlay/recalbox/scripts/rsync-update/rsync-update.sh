#!/bin/bash
log=/recalbox/share/system/logs/updates.log
echo -e "\nUPDATE LOG - `date`\n" >> $log

source /recalbox/scripts/rsync-update/rsync-password.sh
version=`cat /recalbox/recalbox.arch`
echo "begin update" > $log

if (($? != 0)); then
	echo "error : UNABLE TO GET PASSWORD FROM /recalbox/scripts/rsync-update/rsync-password.sh" >> $log
	exit 90
fi

echo "info : will conntect to ${RSYNC_SERVER} with credential : ${RSYNC_USER}" >> $log
echo "info : starting share update" >> $log

rsync -rltXv --exclude-from=/recalbox/scripts/rsync-update/always-exclude.cfg --exclude-from=/recalbox/scripts/rsync-update/exclude-share.cfg rsync://${RSYNC_USER}@${RSYNC_SERVER}/recalbox-share-${version} /recalbox/share >> $log
if (($? != 0)); then
        echo "error : unable to update share" >> $log
        exit 91
fi
echo "info : starting boot update" >> $log
rsync -rltXv --exclude-from=/recalbox/scripts/rsync-update/always-exclude.cfg --exclude-from=/recalbox/scripts/rsync-update/exclude-boot.cfg rsync://${RSYNC_USER}@${RSYNC_SERVER}/recalbox-boot-${version} /boot >> $log
if (($? != 0)); then
        echo "error : unable to update boot" >> $log
        exit 91
fi
echo "info : starting root update" >> $log
rsync -aXv --exclude-from=/recalbox/scripts/rsync-update/always-exclude.cfg --exclude-from=/recalbox/scripts/rsync-update/exclude-root.cfg rsync://${RSYNC_USER}@${RSYNC_SERVER}/recalbox-root-${version} / >> $log
if (($? != 0)); then
        echo "error : unable to update root" >> $log
        exit 91
fi

# POST UPDATE
/recalbox/scripts/rsync-update/updates/00-post-update-script.sh >> $log
error="$?"
if (("$error" != "0")); then
        echo "error : post update error" >> $log
        exit "$error"
fi

echo "info : UPDATE OK" >> $log
