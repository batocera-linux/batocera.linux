#!/bin/bash
recalboxupdateurl="http://archive.recalbox.com"
systemsetting="python /usr/lib/python2.7/site-packages/configgen/settings/recalboxSettings.pyc"

arch=$(cat /recalbox/recalbox.arch)
majorversion=$(cat /recalbox/recalbox.updateversion)
updatetype="`$systemsetting  -command load -key updates.type`"

if test "${updatetype}" != "stable" -a "${updatetype}" != "unstable" -a "${updatetype}" != "beta"
then
    # force a default value in case the value is removed or miswritten
    updatetype="stable"
fi

recallog "------------ Will process to a ${updatetype} upgrade ------------"
# Create download directory
if ! mkdir -p /recalbox/share/system/upgrade
then
    recallog -e "Unable to create upgrade directory"
    exit 1
fi

# Check sizes from header
files="root.tar.xz boot.tar.xz"
size="0"
for file in $files; do
  url="${recalboxupdateurl}/${majorversion}/${arch}/${updatetype}/last/${file}"
  headers=`curl -sfI ${url}`
  if [ $? -ne 0 ];then
    recallog -e "Unable to get headers for ${url}"
    exit 2
  fi
  filesize=`echo "$headers" | grep "Content-Length: " | grep -Po '\d+'`
  if [ $? -ne 0 ];then
    recallog -e "Unable to get size from headers ${url}"
    exit 3
  fi
  size=$(($size + filesize))
done
if [[ "$size" == "0" ]];then
  recallog -e "Download size = 0"
  exit 4
fi

size=$((size / 1024))
recallog "Needed size for upgrade : ${size}kb"

# Getting free space on share
freespace=`df -k /recalbox/share | tail -1 | awk '{print $4}'`
if [ $? -ne 0 ];then
  recallog -e "Unable to get freespace for /recalbox/share"
  exit 5
fi
diff=$((freespace - size))
if [[ "$diff" -lt "0" ]]; then
  recallog -e "Not enough space on /recalbox/share to download the update"
  exit 6
fi
recallog "Will download ${size}kb of files in /recalbox/share/system/upgrade where ${freespace}kb is available. Free disk space after operation : ${diff}kb"

# Downloading files
function cleanBeforeExit {
  rm -rf /recalbox/share/system/upgrade/*
  exit $1
}
files="boot.tar.xz root.tar.xz"
for file in $files; do
  url="${recalboxupdateurl}/${majorversion}/${arch}/${updatetype}/last/${file}"
  if ! curl -fs "${url}" -o "/recalbox/share/system/upgrade/${file}";then
    recallog -e "Unable to download file ${url}"
    cleanBeforeExit 7
  fi
  recallog "${url} downloaded"
done

recallog -e "All files downloaded, ready for upgrade on next reboot"
exit 0
