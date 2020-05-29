#!/usr/bin/env python

import batoceraFiles
import os
from Emulator import Emulator
from settings.unixSettings import UnixSettings

def generateLinappleConfig(rom, playersControllers, gameResolution):
    # conf file
    try:
        linappleConfig = UnixSettings(batoceraFiles.linappleConfigFile, separator=' ')
    except UnicodeError:
        # remove it and try again
        os.remove(batoceraFiles.linappleConfigFile)
        linappleConfig = UnixSettings(batoceraFiles.linappleConfigFile, separator=' ')

    # Rom
    linappleConfig.save('Disk Image 1', rom)

    # Joysticks, those sticks of joy! There may be 2 joysticks at the same time
    #
    # "Joystick 0" specifies the types of first first joystick.
    #
    # Possible values are:
    #  0 - joystick disabled
    #  1 - use PC joystick #1 or #2, for corresponding joystick
    #  2 - Keyboard standard
    #  3 - Keyboard centered
    #  4 - Use mouse as a joystick. Rather interesting thing, try it. Useful in Fantavision(tm)by Broderbund Software
    #
    # When joysticks used as a keyboard, they are stuck to Numpad keys (1-9 - axis movement, 0 - button1, . - button2)
    # When centered used, axis of joystick will be centered after releasing any cursor (Numpad 1..9) key.
    # Otherwise it assumed to be pressed always.
    #
    # Default is 1.
    #
    # "Joystick 1" specifies the types of the second joystick.
    # Possible values are the same as "Joystick 0".
    # Default is 0.
    linappleConfig.save('Joystick 0', '0')
    linappleConfig.save('Joystick 1', '0')

    # For Joysticks you can define which Joystick index number, axis number, and buttons.
    #
    # Default for Joystick 1 is index 0, axis 0 and 1, buttons 0 and 1.
    # Default for Joystick 2 is index 1, axis 0 and 1, button 0.
    for indexController in playersControllers:
        controller = playersControllers[indexController]
        
        # Enabling control
        linappleConfig.save('Joy{}Index'.format(controller.index),  controller.index)
        linappleConfig.save('Joystick {}'.format(controller.index), '1')

        # Button
        linappleConfig.save('Joy{}Button1'.format(controller.index), controller.inputs["a"].id)
        linappleConfig.save('Joy{}Button2'.format(controller.index), controller.inputs["b"].id)

        # Axis
        linappleConfig.save('Joy{}Axis0'.format(controller.index),   controller.inputs["joystick1left"].id)
        linappleConfig.save('Joy{}Axis1'.format(controller.index),   controller.inputs["joystick1up"].id)
        

        # Enable Quitting the program with by pressing two joystick buttons at the same time
        if (controller.index == 0):
            linappleConfig.save('JoyExitEnable', '1')
            linappleConfig.save('JoyExitButton0', controller.inputs["hotkey"].id)
            linappleConfig.save('JoyExitButton1', controller.inputs["start"].id)

    # Possible values are:
    #   0 - old Apple][, right out of the hands of Steve Wozniak and Steve Jobs in far 1977? year.
    #   1 - Apple][+	- same as Apple][ with somewhat enbettered functionality
    #   2 - Apple//e	- Enhanced Apple][ with 80-column mode and other useful additions
    #   3 - Apple//e enhanced	- currently same as Apple//e? Please, ask Tom Charlesworth about it.
    #
    # Default is 3.
    linappleConfig.save('Computer Emulation', '3')

    # "Sound Emulation" enables audio.
    #
    # Possible values are:
    #  0 - none
    #  1 - use SDL Audio for sounds
    #
    # Default is 1.    
    linappleConfig.save('Sound Emulation', '1')

    # "Soundcard Type" specifies the type of sound card to use.
    #
    # Possible values are:
    #   1 - none (disables audio)
    #   2 - use Mockingboard in Slot 4 (Mockingboard is like SoundBlaster for PC, if you hear about it)
    #   3 - use Phasor in Slot 4. Phasor is also a sort of ancient sound cards. Ahhh, what sounds they have!!!
    #
    # Default is 2.
    linappleConfig.save('Soundcard Type', '2')

    # "Serial Port" joins your Apple][ machine to any device through serial ports.
    #
    # Possible values are:
    #   0        - disabled
    #   1 to 100 - which means device /dev/ttyS0 .. /dev/ttyS99 relatively
    #
    # Default is 0. Needs testing.
    linappleConfig.save('Serial Port', '0')

    # "Emulation Speed" controls the speed of the emulator.
    #
    # Possible values range from 0 to 40 where:
    #    0 - slowest
    #   10 - normal (about 1 MHz)
    #   40 - fastest
    #
    # Default is 10.
    linappleConfig.save('Emulation Speed', '10')

    # "Enhance Disk Speed" disables disk throttling.
    #
    # Possible values are:
    #   0 - disabled, disk spinning speed is like that of a real Apple][
    #   1 - use enhanced disk speed.
    #
    # Default is 1.
    linappleConfig.save('Enhance Disk Speed', '1')

    # "Parallel Printer Filename" specifies the path to use as for printer output.
    # Parallel printer allows you to print any DOS3.3 or Applesoft Basic(tm) output
    # to specified file (after PR#1 at DOS3.3 prompt)
    #
    # Possible values are any valid path.
    #
    # Default is "Printer.txt".
    linappleConfig.save('Parallel Printer Filename', 'Printer.txt')

    # "Slot 6 Autoload" enables automatic insertion of floppy disk images.
    # This is analogous to inserting floppies into an Apple][ before turning it on.
    #
    # Possible values are:
    #   0 - disabled
    #   1 - enabled
    #
    # Default is 0.
    linappleConfig.save('Slot 6 Autoload', '1')
    
    # Save State Filename - file name for saving/loading state with keys F11 and F12 in emulator.
    # Default is none. Note: you can choose it at runtime by pressing F11 (for saving)  or F12 (for loading)
    linappleConfig.save('Save State Filename', '')

    # SaveSate Directory is a directory where current states will be saved by using F11,F12 (or ALT+F11, ALT+F12 keys, or Ctrl+0..9, Ctrl+Shift+0..9)
    #Default is none, which means your home directory
    linappleConfig.save('Save State Directory', batoceraFiles.linapplaSaves)

    # "Save State On Exit" enables automatic saving of the emulator on exit.
    #
    # Possible values are:
    #   0 - disabled
    #   1 - enabled
    #
    # Default value is 0.
    linappleConfig.save('Save State On Exit', '0')

    # "Show Leds" enables displaying LEDs indicating disk access.
    #
    # Possible values are:
    #   0 - disabled
    #   1 - enabled
    #
    # Default is 1.
    linappleConfig.save('Show Leds', '1')

    # Screen properties
    #
    # Note: not all screen sizes can work in full screen mode, so be careful
    # Also if you are using not default mode, the speed of emulator can fall,
    # which can be spotted on old machines
    #
    # "Screen factor" specifies a multipler for the screen size.
    #
    # Any positive value is possible, but the suggested range is 0.3 to 3.0.
    # The value is a multiplier for "Screen Width" and "Screen Height".
    #   < 1.0 will make the screen smaller
    #   > 1.0 will make the screen larger
    #   = 1.0 will keep the screen at 560x384
    #   < 0.1 will be ignored.
    #
    # Default is 0.
    linappleConfig.save('Screen factor', '0')

    # "Screen Width" specifies the horizontal size of the display.
    # Possible values are any positive integer.
    # Value is ignored if "Screen factor" is set to anything >= 0.1.
    # Default is 560.
    #
    # "Screen Height" specifies the vertical size of the display.
    #
    # Possible values are any positive integer.
    # Value is ignored if "Screen factor" is set to anything >= 0.1.
    #
    # For best results, use a height divisible by 192 to avoid moire artifacts when
    # using scanline video effects.
    #
    # Default is 384.
    linappleConfig.save('Screen Width',  gameResolution["width"])
    linappleConfig.save('Screen Height', gameResolution["height"])