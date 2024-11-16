#!/bin/bash

#by cyperghost 11.11.2019

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
#v1.9 - add POWERHAT for Rpi4 OneNineDesign case variants - @dmanlfc
#v2.0 - add DESKPIPRO for Dekpi Pro case (RPi4) - @dmanlfc
#v2.1 - added config switch to avoid double reboots - @dmanlfc
#v2.2 - add PISTATION_LCD support - @dmanlfc
#v2.3 - add ELEMENT14_PI_DESKTOP support - @dmanlfc
#v2.4 - removed code duplicates @lala
#v2.5 - add PIRONMAN case support (RPi4) - @dmanlfc
#v2.6 - add PIRONMAN 5 case support (RPi5) - @dmanlfc
#v2.7 - add Dockerpi Powerboard support - @dmanlfc
#v2.8 - add Argon One RPi5 - @lbrpdx
#v2.9 - add Waveshare WM8960 audio HAT - @dmanlfc

### Array for Powerdevices, add/remove entries here

powerdevices=(
              RETROFLAG "Including NESPi+ SuperPi and MegaPi cases" \
              RETROFLAG_ADV "Advanced script for Retroflag housings" \
              RETROFLAG_GPI "Retroflag GPi case for Raspberry 0" \
              ARGONONE "Fan control for RPi4 & RPi5 Argon One case" \
              KINTARO "SNES style case from SuperKuma aka ROSHAMBO" \
              MAUSBERRY "A neat power device from Mausberry circuits" \
              ONOFFSHIM "The cheapest power device from Pimoroni" \
              POWERHAT "Another cheap power device from OneNineDesign" \
              REMOTEPIBOARD_2003 "Any remote control as pswitch v2013" \
              REMOTEPIBOARD_2005 "Any remote control as pswitch v2015" \
              ATX_RASPI_R2_6 "ATXRaspi is a smart power controller SBC" \
              PIN56ONOFF "py: Sliding switch for proper shutdown" \
              PIN56PUSH "py: Momentary push button for shutdown" \
              PIN356ONOFFRESET "py: Power button and reset button" \
              DESKPIPRO "Fan & power control for RPi4 DeskPi Pro case" \
              PIBOY "Fan & power & pads for Piboy DMG" \
              PISTATION_LCD "Config.txt tweaks to get the display to work" \
              ELEMENT14_PI_DESKTOP "Adds on/off button support" \
              PIRONMAN "Fan, OLED, RGB case support for the Pironman case with RPi4 devices" \
              PIRONMAN5 "Fan, OLED, RGB case support for the Pironman 5 case with RPi5 devices" \
              DOCKERPI_POWERBOARD "Dockerpi Powerboard Hat support for compatible Raspberry Pi boards"
              WM8960_AUDIO_HAT "WM8960 Audio Hat support for compatible Raspberry Pi boards"
             )

#dialog for selecting your switch or power device
function powerdevice_dialog()
{
    local switch cmd button #dialog variabels
    local currentswitch #show current switch

    currentswitch="$(/usr/bin/batocera-settings-get system.power.switch)"
    [[ -z "$currentswitch" ]] && currentswitch="disabled"

    cmd=(dialog --ascii-lines --backtitle "BATOCERA Power Switch Selection Toolset" \
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

function atx_raspi_config()
{
    true
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

function mausberry_config()
{
    true
}

# https://shop.pimoroni.com/products/onoff-shim/
function onoffshim_start()
{
    #------ CONFIG SECTION ------
    #Check if dtooverlay is setted in /boot/config
    #This is needed to do proper restarts/shutdowns
    if ! grep -q "^dtoverlay=gpio-poweroff,gpiopin=$2,active_low=1,input=1" "/boot/config.txt"; then
        mount -o remount, rw /boot
        echo "dtoverlay=gpio-poweroff,gpiopin=$2,active_low=1,input=1" >> "/boot/config.txt"
    fi
    [ $CONF -eq 1 ] && return
    #------ CONFIG SECTION ------


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

function onoffshim_config()
{
    onoffshim_start $@
}

# https://www.raspberrypiplastics.com/power-hat-board
# aka MultiComp Pro Raspberry Pi 4 case
function powerhat_start()
{
    #------ CONFIG SECTION ------
    #Check if dtooverlay is setted in /boot/config.txt
    #This is needed to do proper restarts/shutdowns
    # (GPIO18 default)
    if ! grep -q "^dtoverlay=gpio-poweroff,gpiopin=$1,active_low=0" "/boot/config.txt"; then
        mount -o remount,rw /boot
        echo "" >> "/boot/config.txt"
        echo "[powerhat]" >> "/boot/config.txt"
        echo "dtoverlay=gpio-poweroff,gpiopin=$1,active_low=0" >> "/boot/config.txt"
    fi

    # This is Button command (GPIO17 default)
    if ! grep -q "^dtoverlay=gpio-shutdown,gpiopin=$2,active_low=1,gpio_pull=up" "/boot/config.txt"; then
        mount -o remount,rw /boot
        echo "dtoverlay=gpio-shutdown,gpiopin=$2,active_low=1,gpio_pull=up" >> "/boot/config.txt"
    fi
    [ $CONF -eq 1 ] && return
    #------ CONFIG SECTION ------
}

function powerhat_stop()
{
    # Do nothing to GPIO, handled by power hat
    echo "'power hat' shutdown"
}

function powerhat_config()
{
    powerhat_start $@
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

function msldigital_config()
{
    true
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
        kill $(cat /tmp/rpi-pin356-power.pid)
    fi
}

function pin356_config()
{
    true
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
        kill $(cat /tmp/rpi-pin56-power.pid)
    fi
}

function pin56_config()
{
    true
}

#https://www.retroflag.com
function retroflag_start()
{
    #------ CONFIG SECTION ------
    #Check if dtooverlay is setted in /boot/config -- Do this arch related!
    case $(cat /usr/share/batocera/batocera.arch) in
        bcm2711)
            if ! grep -q "^dtoverlay=gpio-poweroff,gpiopin=4,active_low=1,input=1" "/boot/config.txt"; then
                mount -o remount, rw /boot
                echo "# Overlay setup for proper powercut, needed for Retroflag cases" >> "/boot/config.txt"
                echo "dtoverlay=gpio-poweroff,gpiopin=4,active_low=1,input=1" >> "/boot/config.txt"
            fi
        ;;
    esac
    [ $CONF -eq 1 ] && return
    #------ CONFIG SECTION ------

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

function retroflag_config()
{
    retroflag_start $@
}

# Pi4: https://argon40.com/products/argon-one-v2-case-for-raspberry-pi-4 (but tested on V1 which is EOL now)
# Pi5: https://argon40.com/products/argon-one-v3-case-for-raspberry-pi-5
function argonone_start()
{
    #------ CONFIG SECTION ------
    case $(cat /usr/share/batocera/batocera.arch) in
        bcm2711)
	    if ! grep -q "^dtparam=i2c_arm=on" "/boot/config.txt"; then
		 mount -o remount, rw /boot
		 echo "dtparam=i2c_arm=on" >> "/boot/config.txt"
	    fi
	    if ! grep -q "^dtparam=i2c-1=on" "/boot/config.txt"; then
		 mount -o remount, rw /boot
		 echo "dtparam=i2c-1=on" >> "/boot/config.txt"
	    fi
	    if ! grep -q "^enable_uart=1" "/boot/config.txt"; then
		 mount -o remount, rw /boot
		 echo "enable_uart=1" >> "/boot/config.txt"
	    fi
        ;;
        bcm2712)
	    if ! grep -q "^dtparam=i2c=on" "/boot/config.txt"; then
		 mount -o remount, rw /boot
		 echo "dtparam=i2c=on" >> "/boot/config.txt"
	    fi
	    if ! grep -q "^dtparam=uart0=on" "/boot/config.txt"; then
		 mount -o remount, rw /boot
		 echo "dtparam=uart0=on" >> "/boot/config.txt"
	    fi
        ;;
    esac
    [ $CONF -eq 1 ] && return
    #------ CONFIG SECTION ------

    modprobe i2c-dev
    modprobe i2c-bcm2708
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

function argonone_config()
{
    argonone_start $@
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

function kintaro_config()
{
    true
}

#https://deskpi.com/products/deskpi-pro-for-raspberry-pi-4
function deskpipro_start()
{
    #------ CONFIG SECTION ------
    # Check config.txt for fan & front USB
    if ! grep -q "^dtoverlay=dwc2,dr_mode=host" "/boot/config.txt"; then
        echo "*** Adding DeskPi Pro Case Fan config.txt parameter ***"
        mount -o remount, rw /boot
        # Remove other dtoverlay=dwc2 type configs to avoid conflicts
        sed -i '/dtoverlay=dwc2*/d' /boot/config.txt
        echo "" >> "/boot/config.txt"
        echo "[Deskpi Pro Case]" >> "/boot/config.txt"
        echo "dtoverlay=dwc2,dr_mode=host" >> "/boot/config.txt"
    fi
    # Check config.txt for Infrared
    if grep -Fxq "#dtoverlay=gpio-ir,gpio_pin=17" "/boot/config.txt"; then
        echo "*** Adding DeskPi Pro Case Infrared config.txt parameter ***"
        mount -o remount, rw /boot
        sed -i 's/#dtoverlay=gpio-ir,gpio_pin=17/dtoverlay=gpio-ir,gpio_pin=17/g' /boot/config.txt
    fi
    # Add Infrared parameters
    if ! grep -q "driver = default" "/etc/lirc/lirc_options.conf"; then
        echo "*** Adding DeskPi Pro Case Infrared lirc_options.conf parameters ***"
        mount -o remount, rw /boot
        echo "driver = default" >> "/etc/lirc/lirc_options.conf"
        echo "device = /dev/lirc0" >> "/etc/lirc/lirc_options.conf"
    fi
    # Check if the kernel module is loaded
    if lsmod | grep dwc2 &> /dev/null ; then
        echo "*** dwc2 module is loaded ***"
    else
        echo "*** loading dwc2 module ***"
        modprobe dwc2
    fi
    [ $CONF -eq 1 ] && return
    #------ CONFIG SECTION ------
    echo "*** Starting DeskPi Pro Case Fan ***"
    /usr/bin/pwmFanControl &
}

function deskpipro_stop()
{
    echo "*** Stopping DeskPi Pro Case Fan ***"
    /usr/bin/fanStop && /usr/bin/safecutoffpower
}

function deskpipro_config()
{
    deskpipro_start $@
}

#https://retroflag.com/pistation-case.html
function pistation_start()
{
    #------ CONFIG SECTION ------
    # Check config.txt for fkms
    if ! grep -Fxq "vc4-fkms-v3d-pi4" "/boot/config.txt"; then
        echo "*** Adding PiStation LCD kms config.txt parameter ***"
        mount -o remount, rw /boot
        # Remove default vc4-kms-v3d-pi4 type config to avoid conflict
        sed -i 's/vc4-kms-v3d-pi4/#vc4-kms-v3d-pi4/g' /boot/config.txt
        echo "" >> "/boot/config.txt"
        echo "[PiStation LCD]" >> "/boot/config.txt"
        echo "# we have the use 'fake' kms for the PiStation LCD panel" >> "/boot/config.txt"
        echo "vc4-fkms-v3d-pi4" >> "/boot/config.txt"
        mount -o remount, ro /boot
    fi
    # Check config.txt for EDID
    if ! grep -Fxq "[EDID=YDK-YD2680]" "/boot/config.txt"; then
        echo "*** Adding PiStation LCD EDID config.txt parameter ***"
        mount -o remount, rw /boot
        echo "" >> "/boot/config.txt"
        echo "# PiStation LCD EDID" >> "/boot/config.txt"
        echo "# remove the section below if no longer needed" >> "/boot/config.txt"
        echo "[EDID=YDK-YD2680]" >> "/boot/config.txt"
        echo "hdmi_group=2" >> "/boot/config.txt"
        echo "hdmi_mode=87" >> "/boot/config.txt"
        echo "hdmi_drive=2" >> "/boot/config.txt"
        echo "hdmi_cvt=800 480 60 6 0 0 0" >> "/boot/config.txt"
        echo "" >> "/boot/config.txt"
        mount -o remount, ro /boot
    fi
    [ $CONF -eq 1 ] && return
    #------ CONFIG SECTION ------
}

function pistation_stop()
{
    true # not required
}

function pistation_config()
{
    pistation_start $@
}

#https://www.experimentalpi.com/PiBoy-DMG--Kit_p_18.html
function piboy_start()
{
    PIBOY_CONFIG_FILE=/boot/config.txt
    PIBOY_CHECK=$(tail "${PIBOY_CONFIG_FILE}" | grep PIBOY | sed 's/PIBOY=//g')
    PIBOY_CONFIG='
# ====== PiBoy Case setup section =====
avoid_warnings=2
dtoverlay=vc4-fkms-v3d
hdmi_group=2
hdmi_mode=85
hdmi_drive=2
audio_pwm_mode=2
dtoverlay=audremap,pins_18_19
##Enable DPI gpio
gpio=0-9,12-17,20-25=a2
audio_pwm_mode=2
dtoverlay=audremap,pins_18_19
##DPI LCD settings
dpi_group=2
dpi_mode=87
dpi_output_format=0x070016
dpi_timings=640 1 44 2 42 480 1 19 2 17 0 0 0 85 0 32000000 1
enable_dpi_lcd=1
##Disable ACT LED
dtparam=act_led_trigger=none
dtparam=act_led_activelow=off
##Disable PWR LED
dtparam=pwr_led_trigger=none
dtparam=pwr_led_activelow=off
##Turn off ethernet port LEDs
dtparam=eth_led0=4
dtparam=eth_led1=4
PIBOY=true
# ====== PiBoy Case toggle section ====='

    if test "${PIBOY_CHECK}" = true
    then
        echo "Check Success Piboy is installed"
        python /usr/bin/piboy_fan_ctrl.py &
        python /usr/bin/piboy_aud_ctrl.py &
        python /usr/bin/piboy_power_ctrl.py &
        modprobe xpi_gamecon.ko
    else
        echo "Check Error Piboy is not installed"
        mount -o remount,rw /boot
        sed -i 's/dtoverlay=vc4-kms-v3d/#dtoverlay=vc4-kms-v3d/g' /boot/config.txt
        sed -i 's/dtoverlay=vc4-fkms-v3d/#dtoverlay=vc4-fkms-v3d/g' /boot/config.txt
        echo -e "${PIBOY_CONFIG}" >> "${PIBOY_CONFIG_FILE}" || exit 1
        mount -o remount,ro /boot
        shutdown -h now
    fi
}

function piboy_stop()
{
    /etc/init.d/S31emulationstation stop && echo 0 > /sys/kernel/xpi_gamecon/flags && /sbin/rmmod xpi_gamecon && shutdown -h now
}

function piboy_config()
{
    true
}

#https://au.element14.com/element14/pi-desktop/element-14-pi-desktop-hatencl/dp/2687142?ICID=I-HP-STM7REC-RP-1
function element14_start()
{
    python /usr/bin/element14/restart.py &
}

function element14_stop()
{
    # emulationstartion stop in the python script above, nothing to do here
    true
}

function element14_config()
{
    true
}

#https://github.com/sunfounder/pironman
function pironman_start()
{
    # Ensure we have the Pironman config file
    if [ ! -d "/userdata/system/.config/pironman" ]; then
        mkdir -p "/userdata/system/.config/pironman"
    fi
    if [ ! -f "/userdata/system/.config/pironman/config.txt" ]; then
        cp "/opt/pironman/config.txt" "/userdata/system/.config/pironman/config.txt"
    fi
    #------ CONFIG SECTION ------
    # Check config.txt for i2c
    if ! grep -q "^dtparam=i2c_arm=on" "/boot/config.txt"; then
        echo "*** Adding Pironman i2c config.txt parameter ***"
        mount -o remount, rw /boot
        # Remove other dtparam=i2c_arm type configs to avoid conflicts
        sed -i '/dtparam=i2c_arm*/d' /boot/config.txt
        echo "" >> "/boot/config.txt"
        echo "[Pironman]" >> "/boot/config.txt"
        echo "dtparam=i2c_arm=on" >> "/boot/config.txt"
    fi
    # Check config.txt for spi
    if grep -q "dtparam=spi=" "/boot/config.txt"; then
        echo "*** Enabling Pironman spi config.txt parameter ***"
        mount -o remount,rw /boot
        sed -i 's/^#\?\s*\(dtparam=spi=\)off/\1on/' /boot/config.txt
    else
        echo "*** Adding Pironman spi config.txt parameter ***"
        mount -o remount,rw /boot
        echo "dtparam=spi=on" >> /boot/config.txt
    fi
    # Check config.txt for core_freq
    if grep -q "core_freq=" "/boot/config.txt"; then
        echo "*** Setting Pironman core_freq config.txt parameter ***"
        mount -o remount, rw /boot
        sed -i 's/^\s*#\?\s*\(core_freq=\).*$/\1500/' /boot/config.txt
    else
        echo "*** Adding Pironman core_freq config.txt parameter ***"
        mount -o remount, rw /boot
        echo "core_freq=500" >> /boot/config.txt
    fi
    # Check config.txt for core_freq_min
    if grep -q "core_freq_min=" "/boot/config.txt"; then
        echo "*** Setting Pironman core_freq_min config.txt parameter ***"
        mount -o remount, rw /boot
        sed -i 's/^\s*#\?\s*\(core_freq_min=\).*$/\1500/' /boot/config.txt
    else
        echo "*** Adding Pironman core_freq_min config.txt parameter ***"
        mount -o remount, rw /boot
        echo "core_freq_min=500" >> /boot/config.txt
    fi
    # Check config.txt for power button
    if ! grep -q "^dtoverlay=gpio-poweroff,gpio_pin=26,active_low=0" "/boot/config.txt"; then
        echo "*** Adding Pironman power off config.txt parameter ***"
        mount -o remount, rw /boot
        # Remove other dtoverlay=gpio-poweroff type configs to avoid conflicts
        sed -i '/dtoverlay=gpio-poweroff*/d' /boot/config.txt
        echo "dtoverlay=gpio-poweroff,gpio_pin=26,active_low=0" >> "/boot/config.txt"
    fi
    # Check config.txt for Infrared
    if grep -Fxq "#dtoverlay=gpio-ir,gpio_pin=17" "/boot/config.txt"; then
        echo "*** Adding Pironman infrared config.txt parameter ***"
        mount -o remount, rw /boot
        #Pironman uses gpio 13 not 17
        sed -i 's/#dtoverlay=gpio-ir,gpio_pin=17/dtoverlay=gpio-ir,gpio_pin=13/g' /boot/config.txt
    fi
    [ $CONF -eq 1 ] && return
    #------ CONFIG SECTION ------
    echo "*** Starting Pironman services ***"
    modprobe i2c_dev
    /usr/bin/pironman start
}

function pironman_stop()
{
    echo "*** Stopping Pironman services ***"
    /usr/bin/pironman stop
}

function pironman_config()
{
    pironman_start $@
}

#https://github.com/sunfounder/pironman5
function pironman5_start()
{
    echo "*** Starting Pironman 5 services ***"
    #------ CONFIG SECTION ------
    # Check config.txt for i2c
    if ! grep -q "^dtparam=i2c_arm=on" "/boot/config.txt"; then
        echo "*** Adding Pironman i2c config.txt parameter ***"
        mount -o remount, rw /boot
        # Remove other dtparam=i2c_arm type configs to avoid conflicts
        sed -i '/dtparam=i2c_arm*/d' /boot/config.txt
        echo "" >> "/boot/config.txt"
        echo "[Pironman 5]" >> "/boot/config.txt"
        echo "dtparam=i2c_arm=on" >> "/boot/config.txt"
    fi
    # Check config.txt for spi
    if grep -q "dtparam=spi=" "/boot/config.txt"; then
        echo "*** Enabling Pironman spi config.txt parameter ***"
        mount -o remount,rw /boot
        sed -i 's/^#\?\s*\(dtparam=spi=\)off/\1on/' /boot/config.txt
    else
        echo "*** Adding Pironman spi config.txt parameter ***"
        mount -o remount,rw /boot
        echo "dtparam=spi=on" >> /boot/config.txt
    fi
    # log location
    mkdir -p /var/log/pironman5
    # ensure i2c is running
    modprobe i2c_dev
    # setup user adjustable config file
    site_packages_dir=$(python3 -c "import site; print(site.getsitepackages()[0])")
    mkdir -p $site_packages_dir/pironman5
    ln -sf /userdata/system/configs/pironman5/config.json $site_packages_dir/pironman5/config.json
    # start
    /usr/bin/pironman5 start --background
}

function pironman5_stop()
{
    echo "*** Stopping Pironman 5 services ***"
    /usr/bin/pironman5 stop
}

function pironman5_config()
{
    pironman5_start $@
}

#https://wiki.52pi.com/index.php?title=EP-0104
function powerboard_start() {
    echo "*** Starting Powerboard hat services ***"
    
    #------ CONFIG SECTION ------
    CONFIG_FILE="/boot/config.txt"
    
    # Check if /boot is writable, if not make it writable
    if ! touch "$CONFIG_FILE" >/dev/null 2>&1; then
        echo "*** Mounting /boot as writable ***"
        mount -o remount,rw /boot || {
            echo "Error: Failed to mount /boot as writable"
            return 1
        }
    fi
    
    # Configure I2C
    PARAM="dtparam=i2c_arm"
    # Check for existing parameter (including commented out)
    if grep -q "^#*${PARAM}" "$CONFIG_FILE"; then
        # Parameter exists, check various states
        if grep -q "^#.*${PARAM}=on" "$CONFIG_FILE"; then
            echo "*** Uncommenting i2c configuration ***"
            # Remove the comment from the line
            sed -i "s/^#\(.*${PARAM}=on\)/\1/" "$CONFIG_FILE"
        elif grep -q "^#.*${PARAM}=off" "$CONFIG_FILE"; then
            echo "*** Enabling i2c configuration ***"
            # Remove the commented out disabled line and add enabled one
            sed -i "/^#.*${PARAM}=off/d" "$CONFIG_FILE"
            echo "${PARAM}=on" >> "$CONFIG_FILE"
        elif grep -q "^${PARAM}=off" "$CONFIG_FILE"; then
            echo "*** Enabling i2c configuration ***"
            # Remove the disabled line and add enabled one
            sed -i "/^${PARAM}=off/d" "$CONFIG_FILE"
            echo "${PARAM}=on" >> "$CONFIG_FILE"
        elif grep -q "^${PARAM}=on" "$CONFIG_FILE"; then
            echo "*** I2C already enabled ***"
        fi
    else
        # Parameter doesn't exist at all, append it
        echo "*** Adding i2c configuration ***"
        echo "${PARAM}=on" >> "$CONFIG_FILE"
    fi
    
    # Remount /boot as read-only
    echo "*** Remounting /boot as read-only ***"
    mount -o remount,ro /boot || {
        echo "Error: Failed to remount /boot as read-only"
        return 1
    }
    
    # Ensure i2c is loaded
    echo "*** Loading i2c-dev module ***"
    if ! modprobe i2c_dev; then
        echo "Error: Failed to load i2c_dev module"
        return 1
    fi
    
    # Start appropriate powerboard service based on architecture
    echo "*** Starting Powerboard service ***"
    arch=$(uname -m)
    if [ "$arch" == "aarch64" ]; then
        if [ -x "/usr/sbin/powerboard64" ]; then
            /usr/sbin/powerboard64 &
            echo "*** Started powerboard64 service ***"
        else
            echo "Error: powerboard64 executable not found or not executable"
            return 1
        fi
    else
        if [ -x "/usr/sbin/powerboard32" ]; then
            /usr/sbin/powerboard32 &
            echo "*** Started powerboard32 service ***"
        else
            echo "Error: powerboard32 executable not found or not executable"
            return 1
        fi
    fi
    
    echo "*** Powerboard hat initialization completed ***"
}

function powerboard_stop()
{
    # Handled by the Hat
    true
}

function powerboard_config()
{
    powerboard_start $@
}

function wm8960audiohat_start() {
    echo "*** Starting WM8960 audio hat ***"
    
    #------ CONFIG SECTION ------
    CONFIG_FILE="/boot/config.txt"
    
    # Check if /boot is writable, if not make it writable
    if ! touch "$CONFIG_FILE" >/dev/null 2>&1; then
        echo "*** Mounting /boot as writable ***"
        mount -o remount,rw /boot || {
            echo "Error: Failed to mount /boot as writable"
            return 1
        }
    fi
    
    # Helper function to handle dtparam configuration
    configure_dtparam() {
        local PARAM=$1
        local PARAM_NAME=$2
        
        # Check for existing parameter (including commented out)
        if grep -q "^#*${PARAM}" "$CONFIG_FILE"; then
            if grep -q "^#.*${PARAM}=on" "$CONFIG_FILE"; then
                echo "*** Uncommenting ${PARAM_NAME} ***"
                sed -i "s/^#\(.*${PARAM}=on\)/\1/" "$CONFIG_FILE"
                echo "*** ${PARAM_NAME} parameter uncommented ***"
            elif grep -q "^#.*${PARAM}=off" "$CONFIG_FILE"; then
                echo "*** Removing commented out disabled ${PARAM_NAME} and adding enabled one ***"
                sed -i "/^#.*${PARAM}=off/d" "$CONFIG_FILE"
                echo "${PARAM}=on" >> "$CONFIG_FILE"
                echo "*** ${PARAM_NAME} parameter enabled ***"
            elif grep -q "^${PARAM}=off" "$CONFIG_FILE"; then
                echo "*** Enabling ${PARAM_NAME} ***"
                sed -i "/^${PARAM}=off/d" "$CONFIG_FILE"
                echo "${PARAM}=on" >> "$CONFIG_FILE"
                echo "*** ${PARAM_NAME} parameter enabled ***"
            elif grep -q "^${PARAM}=on" "$CONFIG_FILE"; then
                echo "*** ${PARAM_NAME} parameter already enabled ***"
            fi
        else
            # Parameter doesn't exist at all, append it
            echo "*** Adding ${PARAM_NAME} parameter ***"
            echo "${PARAM}=on" >> "$CONFIG_FILE"
            echo "*** ${PARAM_NAME} parameter added ***"
        fi
    }
    
    # Configure I2C
    configure_dtparam "dtparam=i2c_arm" "WM8960 audio hat i2c"
    
    # Configure I2S
    configure_dtparam "dtparam=i2s" "WM8960 audio hat i2s"
    
    # Configure WM8960 overlay
    OVERLAY="dtoverlay=wm8960-soundcard"
    if grep -q "^#*${OVERLAY}" "$CONFIG_FILE"; then
        if grep -q "^#.*${OVERLAY}" "$CONFIG_FILE"; then
            echo "*** Uncommenting WM8960 soundcard overlay ***"
            sed -i "s/^#\(.*${OVERLAY}\)/\1/" "$CONFIG_FILE"
            echo "*** WM8960 soundcard overlay uncommented ***"
        else
            echo "*** WM8960 soundcard overlay already configured ***"
        fi
    else
        echo "*** Adding WM8960 soundcard overlay ***"
        echo "$OVERLAY" >> "$CONFIG_FILE"
        echo "*** WM8960 soundcard overlay added ***"
    fi

    # Remount /boot as read-only
    echo "*** Remounting /boot as read-only ***"
    mount -o remount,ro /boot || {
        echo "Error: Failed to remount /boot as read-only"
        return 1
    }
    
    echo "*** WM8960 audio hat initialization completed ***"
    echo "*** If you're seeing this message you should reboot your device ***"
}

function wm8960audiohat_stop()
{
    # Handled by the hat
    true
}

function wm8960audiohat_config()
{
    wm8960audiohat_start $@
}

#-----------------------------------------
#------------------ MAIN -----------------
#-----------------------------------------

# First parameter must be start, stop or config
# Followed by switch parameter from S92switch
# If you start by CLI a dialog will appear

if [[ "$1" == "start" || "$1" == "stop" || "$1" == "config" ]]; then
    [[ -n "$2" ]] && CONFVALUE="$2" || exit 1
    [[ "$1" == "config" ]] && CONF=1 || CONF=0 #config mode
elif [[ -z "$1" ]]; then
    CONFVALUE="--DIALOG"
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
    "POWERHAT")
        powerhat_$1 18 17
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
        pin356_$1
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
    "DESKPIPRO")
        deskpipro_$1
    ;;
    "PIBOY")
        piboy_$1
    ;;
    "PISTATION_LCD")
        pistation_$1
    ;;
    "ELEMENT14_PI_DESKTOP")
        element14_$1
    ;;
    "PIRONMAN")
        pironman_$1
    ;;
    "PIRONMAN5")
        pironman5_$1
    ;;
    "DOCKERPI_POWERBOARD")
        powerboard_$1
    ;;
    "WM8960_AUDIO_HAT")
        wm8960audiohat_$1
    ;;
    "--DIALOG")
        # Go to selection dialog
        switch="$(powerdevice_dialog)"

        # Write values and display MsgBox
        [[ -n "$switch" ]] || { echo "Abort! Nothing changed...."; exit 1; }
        /usr/bin/batocera-settings-set system.power.switch "$switch"
        [[ $? -eq 0 ]] && info_msg="No error! Everything went okay!" || info_msg="An error occurred!"
        dialog --ascii-lines --backtitle "BATOCERA Power Switch Selection Toolkit" \
               --title " STATUS OF NEW VALUE " \
               --msgbox "${info_msg}\n\n$(/usr/bin/batocera-settings-get system.power.switch)" 0 0
    ;;
    --HELP)
        echo "Try: $(basename "$0") {start|stop|config} <value>"
        echo
        echo -e -n "Valid values are:\t"
        for i in $(seq 1 2 ${#powerdevices[@]}); do
            echo -e -n "${powerdevices[i-1]}\n\t\t\t"
        done
        echo
    ;;
    *)
        echo "rpi_gpioswitch: False parameter to S92switch 'start', 'stop' or 'config' cmd. use --help" >&2
        echo "Usage: /etc/init.d/S92switch { start | stop | config } <DEVICE>" >&2
        echo "For setup: /etc/init.d/S92switch setup" >&2
        exit 1
esac
