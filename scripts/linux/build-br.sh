#!/bin/bash -e

if [ "$USER" == "root" ]; then
    echo "You don't need to run this script with root."
fi

ScriptDir="`dirname ${0}`"
. "${ScriptDir}/br-shared.sh"

echo "Building buildroot for ${arch}..."
mkdir -p "${br_build_pwd}"
make O="${br_build_pwd}" "recalbox-${arch}_defconfig"
cd "${br_build_pwd}"
make menuconfig
make savedefconfig
make
cd "${br_pwd}"
echo "Done."
