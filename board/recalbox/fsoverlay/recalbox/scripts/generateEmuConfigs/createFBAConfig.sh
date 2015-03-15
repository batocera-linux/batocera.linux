function createFBAConfig {
   # usage "$1" : guid,  "$2" player
   echo "will generate FBA config for uid $1 and player $2" >> ~/generateconfig.log
   if [[ "$1" != "DEFAULT" ]];then
	uuid="$1"
	player="$2"


	# Read xml of emulationstation
	inputs=`xml sel -T -t -m "//*[@deviceGUID='$uuid']/*" -v "concat(@name,'|',  @type,'|', @id,'|', @value)" -n "$es_input"` 


	#inputsNames=`xml sel -t -v "//*[@deviceGUID='$1']/*/@name" -n < "$es_input"`
	deviceName="$3"


	#`xml sel -t -v "//*[@deviceGUID='$uuid']/@deviceName" -n < "$es_input"`
	IFS=$'\n'

	# fba2x
	declare -A fbabtn
	fbabtn['a']='Y'
	fbabtn['b']='X'
	fbabtn['x']='B'
	fbabtn['y']='A'
	fbabtn['pageup']='L'
	fbabtn['pagedown']='R'
	fbabtn['start']='START'
	fbabtn['select']='SELECT'

	declare -A fba6btn
	fba6btn['a']='L'
	fba6btn['b']='Y'
	fba6btn['x']='X'
	fba6btn['y']='A'
	fba6btn['pageup']='B'
	fba6btn['pagedown']='R'
	fba6btn['start']='START'
	fba6btn['select']='SELECT'

	declare -A fbadir
	fbadir['up']='UP'
	fbadir['down']='DOWN'
	fbadir['left']='LEFT'
	fbadir['right']='RIGHT'

	declare -A fbaaxis
	fbaaxis['up']='UD'
	fbaaxis['left']='LR'
	fbaaxis['down']='UD'
	fbaaxis['right']='LR'

	declare -A fbaHatToAxis
	fbaHatToAxis['1']='UD'
	fbaHatToAxis['2']='LR'
	fbaHatToAxis['4']='UD'
	fbaHatToAxis['8']='LR'

	declare -A fbaspecials
	fbaspecials['start']='QUIT'
	fbaspecials['hotkey']='HOTKEY'

	#6buttons
        for rawinput in $inputs; do
                input=`echo $rawinput | cut -d '|' -f1`
                type=`echo $rawinput | cut -d '|' -f2`
                id=`echo $rawinput | cut -d '|' -f3`
                value=`echo $rawinput | cut -d '|' -f4`

                if [[ ${fbadir[$input]} ]]; then
                        if [[ "$type" == "axis" ]]; then
                                echo "JA_${fbaaxis[$input]}_${player}=${id}" >> "$fba_config_6btn"                            
			elif [[ "$type" == "button" ]];then
                                echo "${fbadir[$input]}_${player}=${id}" >> "$fba_config_6btn"
                        fi
                fi
                if [[ ${fba6btn[$input]} ]]; then
                        echo "${fba6btn[$input]}_${player}=${id}" >> "$fba_config_6btn" 
                fi
                if [[ ${fbaspecials[$input]} ]] && [ "$player" == "1" ]; then
                        echo "${fbaspecials[$input]}=${id}" >> "$fba_config_6btn" 
                fi
        done
	#4 buttons
	for rawinput in $inputs; do
		input=`echo $rawinput | cut -d '|' -f1`
		type=`echo $rawinput | cut -d '|' -f2`
		id=`echo $rawinput | cut -d '|' -f3`
		value=`echo $rawinput | cut -d '|' -f4`
		if [[ ${fbadir[$input]} ]]; then
			if [[ "$type" == "axis" ]]; then
			        echo "JA_${fbaaxis[$input]}_${player}=${id}"  >> "$fba_config"
			elif [[ "$type" == "button" ]];then
			        echo "${fbadir[$input]}_${player}=${id}" >> "$fba_config"
			fi
		fi
		if [[ ${fbabtn[$input]} ]]; then
			echo "${fbabtn[$input]}_${player}=${id}" >> "$fba_config" 
		fi
		if [[ ${fbaspecials[$input]} ]] && [ "$player" == "1" ]; then
		        echo "${fbaspecials[$input]}=${id}" >> "$fba_config" 
		fi
	done
   fi
}

declare -A usedJoysticks

function setFBAJoypadIndexes {
	# 1 trouver les id a partir des noms
	findIdByName "$1"
	joyindex[1]=$joysticksystemindex
	findIdByName "$2"
	joyindex[2]=$joysticksystemindex
	findIdByName "$3"
	joyindex[3]=$joysticksystemindex
	findIdByName "$4"
	joyindex[4]=$joysticksystemindex
	echo "setJoypadIndex for FBA ----------------------------" >> ~/generateconfig.log
	echo "	I have for player 1 : index=${joyindex[1]} for joystick $1" >> ~/generateconfig.log
	echo "	I have for player 2 : index=${joyindex[2]} for joystick $2" >> ~/generateconfig.log
	echo "	I have for player 3 : index=${joyindex[3]} for joystick $3" >> ~/generateconfig.log
	echo "	I have for player 4 : index=${joyindex[4]} for joystick $4" >> ~/generateconfig.log
	for joueur in {1..4}; do
		if (( "${joyindex[$joueur]}" >= "0" ));then
			echo "writing given config for player $joueur" >> ~/generateconfig.log
		        echo "SDLID_${joueur}=${joyindex[$joueur]}" >> "$fba_config"
		        echo "SDLID_${joueur}=${joyindex[$joueur]}" >> "$fba_config_6btn"
		fi
	done
}

function setFBAExtraConfig {
	#smoothing enable by default
	settingsSmooth=`cat "$es_settings" | sed -n 's/.*name="Smooth" value="\(.*\)".*/\1/p'`
	if [ "$settingsSmooth" == "" ];then
        	settingsSmooth="true"
	fi
	if [ "$settingsSmooth" == "false" ];then
		sed -i "s/DisplaySmoothStretch=.*/DisplaySmoothStretch=0/g" "$fba_config"
		sed -i "s/DisplaySmoothStretch=.*/DisplaySmoothStretch=0/g" "$fba_config_6btn"
	fi

	settingsGameRatio=`cat "$es_settings" | sed -n 's/.*name="GameRatio" value="\(.*\)".*/\1/p'`
        if [ "$settingsGameRatio" == "" ] || [ "$settingsGameRatio" == "auto" ];then
                settingsGameRatio="4/3"
        fi
        echo $settingsGameRatio
        if [ "$settingsGameRatio" == "4/3" ];then
                sed -i "s/MaintainAspectRatio=.*/MaintainAspectRatio=1/g" "$fba_config"
                sed -i "s/MaintainAspectRatio=.*/MaintainAspectRatio=1/g" "$fba_config_6btn"
        elif [ "$settingsGameRatio" == "16/9" ];then
                sed -i "s/MaintainAspectRatio=.*/MaintainAspectRatio=0/g" "$fba_config"
                sed -i "s/MaintainAspectRatio=.*/MaintainAspectRatio=0/g" "$fba_config_6btn"
        fi
}
