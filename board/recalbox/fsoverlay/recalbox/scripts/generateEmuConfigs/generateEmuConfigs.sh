#!/bin/bash

# reste a faire GBA

if [ -z "$1" ] || [ -z "$2" ] || [ -z "$3" ] || [ -z "$4" ] || [ -z "$5" ] || [ -z "$6" ] || [ -z "$7" ] || [ -z "$8" ] || [ -z "$9" ] || [ -z "${10}" ] || [ -z "${11}" ] || [ -z "${12}" ] || [ -z "${13}" ]; then
	echo "Usage : generateConfig.sh guid1 udevindex1 name1 guid2 udevindex2 name2 guid3 udevindex3 name3 guid4 udevindex4 name4 system"
	exit -1
fi
a_guid1="$1"
a_udev1="$2"
a_name1="$3"
a_guid2="$4"
a_udev2="$5"
a_name2="$6"
a_guid3="$7"
a_udev3="$8"
a_name3="$9"
a_guid4="${10}"
a_udev4="${11}"
a_name4="${12}"
a_system="${13}"


es_input="/root/.emulationstation/es_input.cfg"
es_settings="/root/.emulationstation/es_settings.cfg"

fba_config_dir="/recalbox/configs/fba/"
fba_original="$fba_config_dir/fba2x.cfg.origin"
fba_original_6btn="$fba_config_dir/fba2x6btn.cfg.origin"
fba_config="$fba_config_dir/fba2x.cfg"
fba_config_6btn="$fba_config_dir/fba2x6btn.cfg"


retroinputdir="/recalbox/configs/retroarch/inputs/"
retroarch_config_dir="/recalbox/configs/retroarch/"
retroarch_original="$retroarch_config_dir/retroarchcustom.cfg.origin"
retroarch_config="$retroarch_config_dir/retroarchcustom.cfg"

mupen64_config="/recalbox/configs/mupen64/mupen64plus.cfg"

systemsetting=/recalbox/scripts/systemsetting.sh


# restoring config
cp "$fba_original" "$fba_config"
cp "$fba_original_6btn" "$fba_config_6btn"
if [ ! -f "$retroarch_config" ];then
	cp "$retroarch_original" "$retroarch_config"
fi

my_dir="$(dirname "$0")"

source "$my_dir/findIdByName.sh"
source "$my_dir/createFBAConfig.sh"
source "$my_dir/createRetroarchConfig.sh"
source "$my_dir/createMupen64Config.sh"

#clean logs
rm ~/generateconfig.log

settings_fba="`$systemsetting get fba_emulator`"
if [ "$a_system" == "fba" ] && [[ "$settings_fba" != "libretro" ]];then
    createFBAConfig "$a_guid1" "1" "$a_name1"
    createFBAConfig "$a_guid2" "2" "$a_name2"
    createFBAConfig "$a_guid3" "3" "$a_name3"
    createFBAConfig "$a_guid4" "4" "$a_name4"
    setFBAJoypadIndexes "$a_name1" "$a_name2" "$a_name3" "$a_name4"
    setFBAExtraConfig
elif [ "$a_system" == "neogeo" ];then
    createFBAConfig "$a_guid1" "1" "$a_name1"
    createFBAConfig "$a_guid2" "2" "$a_name2"
    createFBAConfig "$a_guid3" "3" "$a_name3"
    createFBAConfig "$a_guid4" "4" "$a_name4"
    setFBAJoypadIndexes "$a_name1" "$a_name2" "$a_name3" "$a_name4"
    setFBAExtraConfig
elif [ "$a_system" == "n64" ];then
    createMupen64Config "$a_guid1" "1" "$a_udev1"
else
    createRetroarchConfig "$a_guid1" "1" "$a_name1"
    createRetroarchConfig "$a_guid2" "2" "$a_name2"
    createRetroarchConfig "$a_guid3" "3" "$a_name3"
    createRetroarchConfig "$a_guid4" "4" "$a_name4"
    clearRetroarchJoypadIndexes
    setRetroarchJoypadIndexes "$a_udev1" "$a_name1" "$a_udev2" "$a_name2" "$a_udev3" "$a_name3" "$a_udev4" "$a_name4"
    setRetroarchExtraConfigs
fi

if [ "$a_system" == "mame" ];then
        switchHotkeyiMame "$a_guid1"
fi
