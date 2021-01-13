## SEGA MODEL 3 IMPORTANT INFO ##

Put your model3 roms in this directory.

Rom files must have a ".zip" extension from romset mame 0.220.

This allows the Supermodel emulator to use compressed roms.
Files inside the .zip must match the board rom & CRC info expected of the emulator or they will not work.
Each .zip file must contain only one compressed rom and be named correctly for compatibility.

Game Compatibility:
-------------------

Game compatibility can be found here - https://www.supermodel3.com/About.html

The Configuration File:
-----------------------

The configuration file, Supermodel.ini, located in the Config folder (/system/configs/supermodel/), which stores input settings as well as most of what can be set on the command line.

Audio:
------

Sound and music volume can be adjusted during run-time using the F9-F12 keys.
Volume settings can be specified in the configuration file as well, globally for all games or tailored on a game-by-game basis.

Save States And Non-Volatile Memory:
------------------------------------

Save states are fully supported. Up to 10 different slots can be selected with keyboard - F6. To save and restore states, press F5 and F7.
State files are saved in the Saves folder (/saves/supermodel/), which must exist in order for save operations to succeed.
Non-volatile memory (NVRAM) consists of battery-backed backup RAM (typically used for high score data) and an EEPROM (machine settings).
It is saved to the NVRAM folder (/system/configs/supermodel/NVRAM/) each time Supermodel exits and is re-loaded at start-up.
Save states will also save and overwrite NVRAM data.
If you alter any machine settings, loading an earlier state will return them to their former configuration.
Be sure to save these files for future use.

Emulation Exit
--------------

Configuration is set as Select & Start controller buttons.

Troubleshooting:
----------------

See the Supermodel FAQ here - https://www.supermodel3.com/FAQ.html
