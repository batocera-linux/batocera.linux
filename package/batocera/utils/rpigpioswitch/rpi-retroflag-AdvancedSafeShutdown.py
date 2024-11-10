#!/bin/bash
# First script for NESPi-cases for Batocera v41
# Direct Access to gpio-filesystem isn't allowed anymore so gpiod is used
# cyperghost aka crcerror - 10.11.2024

#initialize pins
powerPin=3 #pin 5
ledPin=14 #TXD - pin 8
resetPin=2 #pin 3
powerenPin=4 #pin 7

#initialize GPIO settings
init_pins(){
    chip=0 #Pi0-4
    #chip=4 #Pi5??
    gpioset --bias=pull-up $chip $powerPin=1
    gpioset --bias=pull-up $chip $resetPin=1
    gpioset --drive=open-source $chip $ledPin=1
    gpioset --drive=open-source $chip $powerenPin=1
}

blink_led(){
    for i in 0 1 0 1 0; do
        gpioset --drive=open-source $chip $ledPin=$i
        sleep 0.25
    done
}
    
get_state(){
    power_state=$(gpioget $chip $powerPin)
    reset_state=$(gpioget $chip $resetPin) 
}

wait_for_buttons(){
    gpiomon --num-events=1 -f -s $chip $powerPin $resetPin
    [[ $(gpioget $chip $resetPin) -ne $reset_state ]] && return 0

    #Debounce and check twice
    if [[ $(gpioget $chip $powerPin) -ne $power_state ]]; then
        sleep 1
        [[ $(gpioget $chip $powerPin) -ne $power_state ]] && return 1
    fi
}

init_pins

while true; do   
    sleep 0.5 #debounce
    get_state
    wait_for_buttons
    ret=$?

    case $ret in
        0) #Reset Button
            es_pid=$(batocera-es-swissknife --espid)
            emu_pid=$(batocera-es-swissknife --emupid)
            if [[ $emu_pid -ne 0 ]]; then
                batocera-es-swissknife --emukill
            elif [[ $es_pid -ne 0 ]]; then
                batocera-es-swissknife --restart
            else
                shutdown -r now
            fi
        ;;
        1) #Power Button
           blink_led
           es_pid=$(batocera-es-swissknife --espid)
           if [[ $es_pid -ne 0 ]]; then
                batocera-es-swissknife --shutdown
            else
                shutdown -h now
            fi
        ;;
    esac
done
