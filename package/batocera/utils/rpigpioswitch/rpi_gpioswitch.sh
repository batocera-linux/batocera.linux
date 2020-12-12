#!/bin/bash

#v1.0 // ol style script
#Notes:
#WittyPi makes use of wiringPi (gpio) which may be dropped from further dev

#v1.1 - add dialog to select your switch
#     - cleaned off scripts
#     - $2 argument is parsed by S92switch script now /etc/init.d
#     - added help section, type 'rpi_gpioswitch help'
#     - some other small improvements
#v1.2 - add RETROFLAG power devices (means NESPi+, MegaPi, SuperPi)
#v1.3 - add RETROFLAG_GPI power device, the GameBoy look-a-like-device for Pi0/W
#v1.4 - add RETROFLAG_ADV advanced reset script for NESPi+, MegaPi and SuperPi
#v1.5 - add KINTARO for Kintaro/Roshambo cases
#v1.6 - add ARGONONE for Rpi4 Argon One case fan control - @lbrpdx
#v1.7 - add NESPI4 support - @lala
#v1.8 - removed Witty-Pi (WiringPi package is not anymore!)
#by cyperghost 11.11.2019

#dialog for selecting your switch or power device
function powerdevice_dialog()
{
    local powerdevices #array
    local switch cmd button #dialog variabels
    local currentswitch #show current switch

    currentswitch=$(batocera-settings -r system.power.switch)
    [[ -z $currentswitch || $currentswitch == "#" ]] && currentswitch="disabled"

    powerdevices=(
                  RETROFLAG "Including NESPi+ SuperPi and MegaPi cases" \
                  RETROFLAG_GPI "Retroflag GPi case for Raspberry 0" \
                  KINTARO "SNES style case from SuperKuma aka ROSHAMBO" \
                  MAUSBERRY "A neat power device from Mausberry circuits" \
                  ONOFFSHIM "The cheapest power device from Pimoroni" \
                  REMOTEPIBOARD_2003 "Any remote control as pswitch v2013" \
                  REMOTEPIBOARD_2005 "Any remote control as pswitch v2015" \
                  ATX_RASPI_R2_6 "ATXRaspi is a smart power controller SBC" \
                  PIN56ONOFF "py: Sliding switch for proper shutdown" \
                  PIN56PUSH "py: Momentary push button for shutdown" \
                  PIN356ONOFFRESET "py: Power button and reset button" \
                  ARGONONE "Fan control for RPi4 Argon One case" \
                 )

    cmd=(dialog --backtitle "BATOCERA Power Switch Selection Toolset" \
                --title " SWITCH/POWER DEVICE SETUP " \
                --ok-label "Select" --cancel-label "Abort" \
                --stdout --menu "Currently selected device: $currentswitch" 17 74 14)
    switch=$("${cmd[@]}" "${powerdevices[@]}")
    echo "$switch"
}

# http://lowpowerlab.com/atxraspi/#installation
function atx_raspi_start()
{
    # This is GPIO 7 (pin 26 on the pinout diagram).
    # This is an input from ATXRaspi to the Pi.
    # When button is held for ~3 seconds, this pin will become HIGH signalling to this script to poweroff the Pi.
    SHUTDOWN=$1
    REBOOTPULSEMINIMUM=200        #reboot pulse signal should be at least this long
    REBOOTPULSEMAXIMUM=600        #reboot pulse signal should be at most this long
    echo "$SHUTDOWN" > /sys/class/gpio/export
    echo "in" > /sys/class/gpio/gpio$SHUTDOWN/direction

    # Added reboot feature (with ATXRaspi R2.6 (or ATXRaspi 2.5 with blue dot on chip)
    # Hold ATXRaspi button for at least 500ms but no more than 2000ms and a reboot HIGH pulse of 500ms length will be issued

    # This is GPIO 8 (pin 24 on the pinout diagram).
    # This is an output from Pi to ATXRaspi and signals that the Pi has booted.
    # This pin is asserted HIGH as soon as this script runs (by writing "1" to /sys/class/gpio/gpio8/value)
    BOOT=$2
    echo "$BOOT" > /sys/class/gpio/export
    echo "out" > /sys/class/gpio/gpio$BOOT/direction
    echo "1" > /sys/class/gpio/gpio$BOOT/value

    echo "ATXRaspi shutdown script started: asserted pins ($SHUTDOWN=input,LOW; $BOOT=output,HIGH). Waiting for GPIO$SHUTDOWN to become HIGH..."

    #This loop continuously checks if the shutdown button was pressed on ATXRaspi (GPIO7 to become HIGH), and issues a shutdown when that happens.
    #It sleeps as long as that has not happened.
    while true; do
        shutdownSignal=$(cat /sys/class/gpio/gpio$SHUTDOWN/value)
        if [ $shutdownSignal = 0 ]; then
            /bin/sleep 0.2
        else
            pulseStart=$(date +%s%N | cut -b1-13) # mark the time when Shutoff signal went HIGH (milliseconds since epoch)
            while [ $shutdownSignal = 1 ]; do
                /bin/sleep 0.02
                if [ $(($(date +%s%N | cut -b1-13)-$pulseStart)) -gt $REBOOTPULSEMAXIMUM ]; then
                    echo "ATXRaspi triggered a shutdown signal, halting Rpi ... "
                    touch "/tmp/poweroff.please"
                    poweroff
                    exit
                fi
                shutdownSignal=$(cat /sys/class/gpio/gpio$SHUTDOWN/value)
            done
            #pulse went LOW, check if it was long enough, and trigger reboot
            if [ $(($(date +%s%N | cut -b1-13)-$pulseStart)) -gt $REBOOTPULSEMINIMUM ]; then
                echo "ATXRaspi triggered a reboot signal, recycling Rpi ... "
                reboot
                exit
            fi
        fi
    done
}

function atx_raspi_stop()
{
    # Cleanup GPIO init
    for i in $*; do
        echo "$i" > /sys/class/gpio/unexport
    done
}

# http://mausberry-circuits.myshopify.com/pages/setup
function mausberry_start()
{
    # Init GPIO :
    # $1 is the GPIO pin connected to the lead on switch labeled OUT
    # $2 is the GPIO pin connected to the lead on switch labeled IN
    echo "$1" > /sys/class/gpio/export
    echo "in" > /sys/class/gpio/gpio$1/direction

    echo "$2" > /sys/class/gpio/export
    echo "out" > /sys/class/gpio/gpio$2/direction
    echo "1" > /sys/class/gpio/gpio$2/value

    # Wait for switch off signal
    power=0
    while [ "$power" = "0" ]; do
        sleep 1
        power=$(cat /sys/class/gpio/gpio$1/value)
    done

    # Switch off
    if [ "$?" = "0" ]; then
        touch "/tmp/poweroff.please"
        poweroff
    fi
}

function mausberry_stop()
{
    # Cleanup GPIO init
    for i in $*; do
        echo "$i" > /sys/class/gpio/unexport
    done
}

# https://shop.pimoroni.com/products/onoff-shim/
function onoffshim_start()
{
    #Check if dtooverlay is setted in /boot/config
    #This is needed to do proper restarts/shutdowns
    if ! grep -q "^dtoverlay=gpio-poweroff,gpiopin=$2,active_low=1,input=1" "/boot/config.txt"; then
        mount -o remount, rw /boot
        echo "dtoverlay=gpio-poweroff,gpiopin=$2,active_low=1,input=1" >> "/boot/config.txt"
    fi

    # This is Button command (GPIO17 default)
    echo $1 > /sys/class/gpio/export
    echo in > /sys/class/gpio/gpio$1/direction

    power=$(cat /sys/class/gpio/gpio$1/value)
    [ $power -eq 0 ] && switchtype=1 #Sliding Switch
    [ $power -eq 1 ] && switchtype=0 #Momentary push button

    until [ $power -eq $switchtype ]; do
        power=$(cat /sys/class/gpio/gpio$1/value)
        sleep 1
    done

    # Switch off
    if [ "$?" = "0" ]; then
        touch "/tmp/poweroff.please"
        poweroff
    fi
}

function onoffshim_stop()
{
    # Cleanup GPIO init, default Button command (GPIO 17)
    echo "$1" > /sys/class/gpio/unexport
}

# http://www.msldigital.com/pages/support-for-remotepi-board-2013
# http://www.msldigital.com/pages/support-for-remotepi-board-plus-2015
function msldigital_start()
{
    # Init GPIO :
    # $1 is the GPIO pin receiving the shut-down signal
    echo "$1" > /sys/class/gpio/export
    echo "in" > /sys/class/gpio/gpio$1/direction

    # Wait for switch off signal
    power=0
    while [ "$power" = "0" ]; do
        sleep 1
        power=$(cat /sys/class/gpio/gpio$1/value)
    done

    # Switch off
    if [ "$?" = "0" ]; then
        touch "/tmp/poweroff.please"
        poweroff
    fi
}

function msldigital_stop()
{
    if [ -f "/tmp/shutdown.please" ] || [ -f "/tmp/poweroff.please" ]; then
        if [ -f "/tmp/shutdown.please" ] && [ "$CONFVALUE" = "REMOTEPIBOARD_2005" ]; then
            # Init GPIO
            GPIOpin=15
            echo "$GPIOpin" > /sys/class/gpio/export

            # Execute shutdown sequence on pin
            echo "out" > /sys/class/gpio/gpio$GPIOpin/direction
            echo "1" > /sys/class/gpio/gpio$GPIOpin/value
            usleep 125000
            echo "0" > /sys/class/gpio/gpio$GPIOpin/value
            usleep 200000
            echo "1" > /sys/class/gpio/gpio$GPIOpin/value
            usleep 400000
            echo "0" > /sys/class/gpio/gpio$GPIOpin/value
            sleep 1

            # Uninit GPIO
            echo "$GPIOpin" > /sys/class/gpio/unexport
        fi
        echo "out" > /sys/class/gpio/gpio$1/direction
        echo "1" > /sys/class/gpio/gpio$1/value
        sleep 3
    fi
    # Cleanup GPIO init
    for i in $*; do
        echo "$i" > /sys/class/gpio/unexport
    done
}

function pin356_start()
{
    rpi-pin356-power &
    pid=$!
    echo "$pid" > /tmp/rpi-pin356-power.pid
    wait "$pid"
}

function pin356_stop()
{
    if [[ -f /tmp/rpi-pin356-power.pid ]]; then
        kill `cat /tmp/rpi-pin356-power.pid`
    fi
}

function pin56_start()
{
    mode=$1
    rpi-pin56-power -m "$mode" &
    pid=$!
    echo "$pid" > /tmp/rpi-pin56-power.pid
    wait "$pid"
}

function pin56_stop()
{
    if [[ -f /tmp/rpi-pin56-power.pid ]]; then
        kill `cat /tmp/rpi-pin56-power.pid`
    fi
}

#https://www.retroflag.com
function retroflag_start()
{
    #Check if dtooverlay is setted in /boot/config -- Do this arch related!
    case $(cat /usr/share/batocera/batocera.arch) in
        rpi4)
            if ! grep -q "^dtoverlay=gpio-poweroff,gpiopin=4,active_low=1,input=1" "/boot/config.txt"; then
                mount -o remount, rw /boot
                echo "# Overlay setup for proper powercut, needed for Retroflag cases" >> "/boot/config.txt"
                echo "dtoverlay=gpio-poweroff,gpiopin=4,active_low=1,input=1" >> "/boot/config.txt"
            fi
        ;;
    esac

    #$1 = rpi-retroflag-SafeShutdown/rpi-retroflag-GPiCase/rpi-retroflag-AdvancedSafeShutdown
    "$1" &
    pid=$!
    echo "$pid" > "/tmp/$1.pid"
    wait "$pid"
}

function retroflag_stop()
{
    pid_file="/tmp/$1.pid"
    if [[ -e $pid_file ]]; then
        pid=$(cat $pid_file)
        kill $(pgrep -P $pid)
    fi
}

#https://www.argon40.com/argon-one-raspberry-pi-4-case.html
function argonone_start()
{
    if ! grep -q "^dtparam=i2c_arm=on" "/boot/config.txt"; then
         mount -o remount, rw /boot
         echo "dtparam=i2c_arm=on" >> "/boot/config.txt"
    fi
    if ! grep -q "^dtparam=i2c-1=on" "/boot/config.txt"; then
         mount -o remount, rw /boot
         echo "dtparam=i2c-1=on" >> "/boot/config.txt"
    fi
    modprobe i2c-dev
    modprobe i2c-bcm2835
    # Yes, with kernel 5.4.51 on Batocera-29, this is required
    # Otherwise the kernel module is not correctly loaded
    rmmod i2c_bcm2835
    modprobe i2c-bcm2835
    /usr/bin/rpi-argonone start &
    wait $!
}

function argonone_stop()
{
    pid=$(pgrep -f rpi-argonone | head -n 1)
    if ! [ -z "${pid}" ]; then
         kill -9 "${pid}"
    fi

    if [ -f /tmp/shutdown.please ]; then
        # force a power shutdown from GPIO block
        /usr/bin/rpi-argonone halt &
    else
        # only stop fan (keep power block on)
        /usr/bin/rpi-argonone stop &
    fi
}

#https://www.kintaro.co
function kintaro_start()
{
    rpi-kintaro-SafeShutdown &
    pid=$!
    echo "$pid" > "/tmp/rpi-kintaro-SafeShutdown.pid"
    wait "$pid"
}

function kintaro_stop()
{
    pid_file="/tmp/rpi-kintaro-SafeShutdown.pid"
    if [[ -e $pid_file ]]; then
        kill $(cat $pid_file)

    fi
}

#-----------------------------------------
#------------------ MAIN -----------------
#-----------------------------------------

# First parameter must be start or stop
# Followed by switch parameter from S92switch
# If you start by CLI a dialog will appear

if [[ "$1" == "start" || "$1" == "stop" ]]; then
    [[ -n "$2" ]] || exit 1
    CONFVALUE="$2"
elif [[ -z "$1" ]]; then
    CONFVALUE="DIALOG"
elif [[ "${1^^}" =~ "HELP" ]]; then
    CONFVALUE="--HELP"
else
    exit 1
fi

case "$CONFVALUE" in

    "ATX_RASPI_R2_6")
        atx_raspi_$1 7 8
    ;;
    "MAUSBERRY")
        mausberry_$1 23 24
    ;;
    "ONOFFSHIM")
        onoffshim_$1 17 4
    ;;
    "REMOTEPIBOARD_2003")
        msldigital_$1 22
    ;;
    "REMOTEPIBOARD_2005")
        msldigital_$1 14
    ;;
    "PIN56PUSH"|"PIN56ONOFF")
        pin56_$1
    ;;
    "PIN356ONOFFRESET")
        pin356_$1 noparam
    ;;
    "RETROFLAG")
        retroflag_$1 rpi-retroflag-SafeShutdown
    ;;
    "RETROFLAG_GPI")
        retroflag_$1 rpi-retroflag-GPiCase
    ;;
    "RETROFLAG_ADV")
        retroflag_$1 rpi-retroflag-AdvancedSafeShutdown
    ;;
    "ARGONONE")
        argonone_$1
    ;;
    "KINTARO")
        kintaro_$1
    ;;
    "DIALOG")
        # Go to selection dialog
        switch="$(powerdevice_dialog)"

        # Write values and display MsgBox
        [[ -n $switch ]] || { echo "Abort! Nothing changed...."; exit 1;}
        batocera-settings -w system.power.switch -v "$switch"
        [[ $? -eq 0 ]] && info_msg="No error! Everything went okay!" || info_msg="An error occurred!"
        dialog --backtitle "BATOCERA Power Switch Selection Toolkit" \
               --title " STATUS OF NEW VALUE " \
               --msgbox "${info_msg}\n\n$(batocera-settings status system.power.switch)" 0 0
    ;;
    --HELP|*)
        [[ $CONFVALUE == "--HELP" ]] || echo "Wrong argument given to 'start' or 'stop' parameter"
        echo "Try: $(basename "$0") {start|stop} <value>"
        echo
        echo -e -n "Valid values are:\t"
        for i in $(seq 1 2 ${#powerdevices[@]}); do
            echo -e -n "${powerdevices[i-1]}\n\t\t\t"
        done
        echo
    ;;
esac
