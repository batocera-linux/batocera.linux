Adafruit-Retrogame
==================

Raspberry Pi GPIO-to-USB utility for classic game emulators.

How-to: http://learn.adafruit.com/retro-gaming-with-raspberry-pi

Pre-built version supports the default pin/key mapping shown in the tutorial. For other layouts, edit retrogame.c.

Retrogame2PlayersPi2
===================

Raspberry Pi GPIO-to-USB utility for classic game emulators.

Compilation
===========

````
$ git clone https://github.com/ian57/Recalbox-Retrogame-2Players-Pi2
$ cd Raspicade-Retrogame-2Player-Pi2
$ make
````

Pinout Mapping
==============

````
Player 1 :
GPIO 02 -> KEY_UP       // Up
GPIO 03 -> KEY_DOWN     // Down
GPIO 04 -> KEY_LEFT     // Left Joystick (4 pins)
GPIO 17 -> KEY_RIGHT    // Right
GPIO 27 -> KEY_LEFTCTRL // Button 1
GPIO 22 -> KEY_LEFTALT  // Button 2
GPIO 10 -> KEY_SPACE    // Button 3
GPIO 09 -> KEY_LEFTSHIFT// Button 4
GPIO 11 -> KEY_Z        // Button 5
GPIO 05 -> KEY_X        // Button 6
GPIO 06 -> KEY_1        // Button Start P1
GPIO 13 -> KEY_5        // Button Coins/Credits P1

Player 2 :
GPIO 18 -> KEY_R        // Up
GPIO 23 -> KEY_F        // Down
GPIO 24 -> KEY_D        // Left Joystick (4 pins)
GPIO 25 -> KEY_G        // Right
GPIO 08 -> KEY_A        // Button 1
GPIO 07 -> KEY_S        // Button 2
GPIO 12 -> KEY_Q        // Button 3
GPIO 16 -> KEY_W        // Button 4
GPIO 20 -> KEY_E        // Button 5
GPIO 21 -> KEY_T        // Button 6
GPIO 19 -> KEY_2        // Button Start P2
GPIO 26 -> KEY_6        // Button Coins/Credits P2
GPIO 15 -> KEY_ESC      // Button to quit emultors/programs 
````

Maintaining Start P1 + Coins/Credits P1 more than 1 seconds will produce "KEY_ESC" (Escape Key).

Installation
============

Now we have configure to allow retrogame to work and be launched at startup. As in http://learn.adafruit.com/retro-gaming-with-raspberry-pi/buttons, you make

Retrogame requires the uinput kernel module. This is already present on the system but isn't enabled by default. For testing, you can type:

````
sudo modprobe uinput
````

To make this persistent between reboots, append a line to /etc/modules (or edit the file) :

````
sudo sh -c 'echo uinput >> /etc/modules'
````

Now we're in good shape to test it! Retrogame needs to be run as root (need access to memory), i.e.:

````
sudo ./retrogame
````

Give it a try. If it seems to be working, press control+C to stop the program and we'll then set up the system to launch this automatically in the background at startup.

````
sudo nano /etc/rc.local
````

Before the final "exit 0" line, insert this line:

````
/home/pi/Recalbox-Retrogame-2Players-Pi2/retrogame &

````
If you placed the software in a different location, this line should be changed accordingly. "sudo" isn't necessary here because the rc.local script is already run as root.

Reboot the system to test the startup function:

````
sudo reboot
````

The software will now be patiently waiting in the background, ready for use with any emulators.

Each emulator will have its own method for configuring keyboard input. Set them up so the keys match your controller outputs. Up/down/left/right from the arrow keys is a pretty common default among these programs, but the rest will usually require some tweaking.

Arcade Wiring
=============

See https://github.com/ian57/Raspicade-Retrogame-2Player-BPlus/wiki



