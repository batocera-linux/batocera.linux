	declare -A retroarchbtn
	retroarchbtn['a']='a'
	retroarchbtn['b']='b'
	retroarchbtn['x']='x'
	retroarchbtn['y']='y'
	retroarchbtn['pageup']='l'
	retroarchbtn['pagedown']='r'
	retroarchbtn['l2']='l2'
	retroarchbtn['r2']='r2'
	retroarchbtn['start']='start'
	retroarchbtn['select']='select'
	#retroarchbtn['hotkey']='enable_hotkey'

	declare -A retroarchdir
	retroarchdir['up']='up'
	retroarchdir['down']='down'
	retroarchdir['left']='left'
	retroarchdir['right']='right'

        declare -A retroarchjoysticks
        retroarchjoysticks['joystickup']='l_y'
        retroarchjoysticks['joystickleft']='l_x'

        declare -A retroarchhat
        retroarchhat['1']='up'
        retroarchhat['2']='right'
        retroarchhat['4']='down'
        retroarchhat['8']='left'

	declare -A retroarchspecials
	retroarchspecials['x']='load_state'
	retroarchspecials['y']='save_state'
	retroarchspecials['pageup']='screenshot'
	retroarchspecials['b']='menu_toggle'
	retroarchspecials['start']='exit_emulator'

	retroarchspecials['up']='state_slot_increase'
	retroarchspecials['down']='state_slot_decrease'
	retroarchspecials['left']='rewind'
	retroarchspecials['right']='hold_fast_forward'

	declare -A typetoname
	typetoname['button']='btn'
	typetoname['hat']='btn'
	typetoname['axis']='axis'
	typetoname['key']='key'

function createRetroarchConfig {
    if [[ "$1" != "DEFAULT" ]];then
        uuid="$1"
	player="$2"

        # Read xml of emulationstation
        inputs=`xml sel -T -t -m "//*[@deviceGUID='$uuid']/*" -v "concat(@name,'|',  @type,'|', @id,'|', @value)" -n "$es_input"`

        deviceName="$3"
	#`xml sel -t -v "//*[@deviceGUID='$uuid']/@deviceName" -n < "$es_input"`
        IFS=$'\n'


	# Retroarch
	# Files
	configfile="${retroinputdir}/${deviceName}.cfg"

	echo "input_device = \"$deviceName\"" > "$configfile"
	#echo "input_player${player}_device = \"$deviceName\"" >> $retroarch_config

	echo "input_driver = \"udev\"" >> "$configfile"
	
	onlyjoystick="1"
        for rawinput in $inputs; do
                input=`echo $rawinput | cut -d '|' -f1`
                type=`echo $rawinput | cut -d '|' -f2`
                id=`echo $rawinput | cut -d '|' -f3`
                originid=$id
                value=`echo $rawinput | cut -d '|' -f4`
		if [ "$type" == "axis" ]; then
			if [[ "$value" == "-1" ]]; then
				id="-$id"
			else 
				id="+$id"
			fi
		fi

		if [[ ${retroarchbtn[$input]} ]]; then
			echo "input_${retroarchbtn[$input]}_btn = $id" >> "$configfile"
		fi

		if [[ "$type" == "button" ]] || [[ "$type" == "axis" ]]; then
			if [[ ${retroarchdir[$input]} ]]; then
				echo "input_${retroarchdir[$input]}_${typetoname[$type]} = $id" >>  "$configfile"
				if [[ "$type" == "button" ]];then
					onlyjoystick="0"
				fi
			fi
		fi
		if [[ "$type" == "hat" ]]; then
			#checking if dir
                        if [[ ${retroarchdir[$input]} ]]; then
                                echo "input_${retroarchhat[$value]}_btn = h${id}${retroarchhat[$value]}" >>  "$configfile"
                        fi
                fi

		if [[ ${retroarchspecials[$input]} ]];  then
			echo "input_${retroarchspecials[$input]}_${typetoname[$type]} = $id" >>  "$configfile"
		fi
		if [[ $input == "hotkey" ]] && [ "$player" == "1" ]; then
			sed -i "s/input_enable_hotkey_.*/input_enable_hotkey_${typetoname[$type]} = $id/g" "$retroarch_config"
		fi
		# Gestion des joystick supplementaires
                if [[ ${retroarchjoysticks[$input]} ]] && [[ "$type" == "axis" ]];then
                        echo "input_${retroarchjoysticks[$input]}_minus_${typetoname[$type]} = $id" >>  "$configfile"
                        if [[ "$value" == "-1" ]]; then
                                newaxis="+$originid"
                        else
                                newaxis="-$originid"
                        fi
                        echo "input_${retroarchjoysticks[$input]}_plus_${typetoname[$type]} = $newaxis" >>  "$configfile"
                fi
	done
	if [[ "$onlyjoystick" == "1" ]]; then
                sed -i "s/input_player${player}_analog_dpad_mode.*/input_player${player}_analog_dpad_mode = \"0\"/g" "$retroarch_config"
        else
                sed -i "s/input_player${player}_analog_dpad_mode.*/input_player${player}_analog_dpad_mode = \"1\"/g" "$retroarch_config"
        fi
       	echo "Retroarch configuration ok "
	fi
}


declare -A usedJoysticks

function clearRetroarchJoypadIndexes {
	sed -i "/input_player._joypad_index/d" "$retroarch_config"
}

function setRetroarchJoypadIndexes {
	# 1 trouver les id a partir des noms
	udev[1]="$1"
	udev[2]="$3"
	udev[3]="$5"
	udev[4]="$7"
	echo "setJoypadIndex Retroarch ----------------------------" >> ~/generateconfig.log
	echo "	I have for player 1 : index=${udev[1]} for joystick $2" >> ~/generateconfig.log
	echo "	I have for player 2 : index=${udev[2]} for joystick $4" >> ~/generateconfig.log
	echo "	I have for player 3 : index=${udev[3]} for joystick $6" >> ~/generateconfig.log
	echo "	I have for player 4 : index=${udev[4]} for joystick $8" >> ~/generateconfig.log
        for joueur in {1..4}; do
		if (( "${udev[$joueur]}" >= "0" ));then
				echo "writing given config for player $joueur" >> ~/generateconfig.log
			        echo "input_player${joueur}_joypad_index = ${udev[$joueur]}" >> "$retroarch_config" 
				conf["${udev[$joueur]}"]=1
		fi
	done

	echo "Finishing config" >> ~/generateconfig.log
	for joueur in {1..4}; do
		if [ "${udev[$joueur]}" == "-1" ]; then
			echo "So it will be default configuration for player $joueur " >> ~/generateconfig.log
			for pad in {0..10}; do
				if [[ -z "${conf[$pad]}" ]];then
					echo "pad $pad is free , writing in config" >> ~/generateconfig.log
	                        	echo "input_player${joueur}_joypad_index = $pad" >> "$retroarch_config"
					conf[$pad]=1
					break
				fi
			done
		fi
	done

}

function setRetroarchExtraConfigs {
        settingsSmooth=`cat "$es_settings" | sed -n 's/.*name="Smooth" value="\(.*\)".*/\1/p'`
        if [ "$settingsSmooth" == "" ];then
                settingsSmooth="true"
        fi
        if [ "$settingsSmooth" == "false" ];then
                sed -i "s/#\?video_smooth =.*/video_smooth = false/g" "$retroarch_config"
        fi
        if [ "$settingsSmooth" == "true" ];then
                sed -i "s/#\?video_smooth =.*/video_smooth = true/g" "$retroarch_config"
        fi
        settingsGameRatio=`cat "$es_settings" | sed -n 's/.*name="GameRatio" value="\(.*\)".*/\1/p'`
        if [ "$settingsGameRatio" == "" ] || [ "$settingsGameRatio" == "auto" ];then
                settingsGameRatio="4/3"
        fi
        if [ "$settingsGameRatio" == "4/3" ];then
                sed -i "s/#\?aspect_ratio_index =.*/aspect_ratio_index = 0/g" "$retroarch_config"
        elif [ "$settingsGameRatio" == "16/9" ];then
                sed -i "s/#\?aspect_ratio_index =.*/aspect_ratio_index = 1/g" "$retroarch_config"
        fi


}

function switchHotkeyiMame {

        uuid="$1"
        hotkey=`xml sel -T -t -m "//*[@deviceGUID='$uuid']/*[@name='hotkey']" -v "@id" -n "$es_input"` || exit 1
        select=`xml sel -T -t -m "//*[@deviceGUID='$uuid']/*[@name='select']" -v "@id" -n "$es_input"` || exit 1

        if [[ "$hotkey" == "$select" ]]; then
                r1=`xml sel -T -t -m "//*[@deviceGUID='$uuid']/*[@name='pagedown']" -v "@id" -n "$es_input"`
                r1type=`xml sel -T -t -m "//*[@deviceGUID='$uuid']/*[@name='pagedown']" -v "@type" -n "$es_input"`
                sed -i "s/input_enable_hotkey.*/input_enable_hotkey_${typetoname[$r1type]} = $r1/g" "$retroarch_config"
        fi
}
