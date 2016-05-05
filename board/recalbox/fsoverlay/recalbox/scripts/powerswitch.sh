#!/bin/bash

# http://lowpowerlab.com/atxraspi/#installation
atx_raspi_start()
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

atx_raspi_stop()
{
    # Cleanup GPIO init
    for i in $*; do
        echo "$i" > /sys/class/gpio/unexport
    done
}

# http://mausberry-circuits.myshopify.com/pages/setup
mausberry_start()
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

mausberry_stop()
{
    # Cleanup GPIO init
    for i in $*; do
        echo "$i" > /sys/class/gpio/unexport
    done
}

# http://www.msldigital.com/pages/support-for-remotepi-board-2013
# http://www.msldigital.com/pages/support-for-remotepi-board-plus-2015
msldigital_start()
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

msldigital_stop()
{
    if [ -f "/tmp/shutdown.please" -o -f "/tmp/poweroff.please" ]; then
        if [ -f "/tmp/shutdown.please" -a "$CONFVALUE" = "REMOTEPIBOARD_2005" ]; then
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

pin356_start()
{
	python /recalbox/scripts/rpi-pin356-power.py &
    pid=$!
    echo "$pid" > /tmp/rpi-pin356-power.pid
    wait "$pid"
}
pin356_stop()
{
    if [[ -f /tmp/rpi-pin356-power.pid ]]; then
        kill `cat /tmp/rpi-pin356-power.pid`
    fi
}

pin56_start()
{
    mode=$1
    python /recalbox/scripts/rpi-pin56-power.py -m "$mode" &
    pid=$!
    echo "$pid" > /tmp/rpi-pin56-power.pid
    wait "$pid"
}
pin56_stop()
{
    if [[ -f /tmp/rpi-pin56-power.pid ]]; then
        kill `cat /tmp/rpi-pin56-power.pid`
    fi
}

# First parameter must be start or stop
if [[ "$1" != "start" && $1 != "stop" ]]; then
    exit 1
fi

CONFFILE="/recalbox/share/system/recalbox.conf"
CONFPARAM="system.power.switch" 
CONFVALUE=
if [ -e $CONFFILE ]; then
    CONFVALUE=$(sed -rn "s/^$CONFPARAM=(\w*)\s*.*$/\1/p" $CONFFILE | tail -n 1)
fi

case "$CONFVALUE" in
    "ATX_RASPI_R2_6")
        atx_raspi_$1 7 8
    ;;
    "MAUSBERRY")
        mausberry_$1 23 24
    ;;
    "REMOTEPIBOARD_2003")
        msldigital_$1 22
    ;;
    "REMOTEPIBOARD_2005")
        msldigital_$1 14
    ;;
    "PIN56ONOFF")
        pin56_$1 onoff
    ;;
    "PIN56PUSH")
        echo "will start pin56_$1"
        pin56_$1 push
    ;;
    "PIN356ONOFFRESET")
        echo "will start pin356_$1"
        pin356_$1 noparam
    ;;
esac
