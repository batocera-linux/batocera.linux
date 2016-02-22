#!/bin/bash

recalboxupdateurl="http://archive.recalbox.com"
systemsetting="python /usr/lib/python2.7/site-packages/configgen/settings/recalboxSettings.pyc"

arch=$(cat /recalbox/recalbox.arch)
majorversion=4
updatetype="`$systemsetting  -command load -key updates.type`"

if test "${updatetype}" != "stable" -a "${updatetype}" != "unstable" -a "${updatetype}" != "beta"
then
    # force a default value in case the value is removed or miswritten
    updatetype="stable"
fi

if ! mkdir -p /recalbox/share/system/upgrade
then
    exit 1
fi

if ! wget "${recalboxupdateurl}/${majorversion}/${arch}/${updatetype}/last/boot.tar.xz" -O /recalbox/share/system/upgrade/boot.tar.xz.part
then
    exit 1
fi

if ! wget "${recalboxupdateurl}/${majorversion}/${arch}/${updatetype}/last/root.tar.xz" -O /recalbox/share/system/upgrade/root.tar.xz.part
then
    rm "/recalbox/share/system/upgrade/boot.tar.xz.part"
    exit 1
fi

if ! mv /recalbox/share/system/upgrade/boot.tar.xz.part /recalbox/share/system/upgrade/boot.tar.xz
then
    rm /recalbox/share/system/upgrade/boot.tar.xz.part
    rm /recalbox/share/system/upgrade/root.tar.xz.part
    exit 1
fi

if ! mv /recalbox/share/system/upgrade/root.tar.xz.part /recalbox/share/system/upgrade/root.tar.xz
then
    rm /recalbox/share/system/upgrade/boot.tar.xz
    rm /recalbox/share/system/upgrade/root.tar.xz.part
    exit 1
fi

exit 0
