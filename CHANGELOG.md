# Change Log
All notable changes to this project will be documented in this file.
This project adheres to [Semantic Versioning](http://semver.org/).

## [Unrelease][unreleased]
- Fixing Makelfiles for compilation of libretro-lutro for the bump to release  2377dd37ad3bd37ddef9fc37742bba2531a78407 
- Bump retroarch to last release due to integration of libretro-imageviewer in its cores, and delation of the libretro-imageviewer repos
- Update Mame2003 core to get the mame2003-skip_warnings and avoid splash screen
- New emulator : PPSSPP
- Add Mayflash NES/SNES and SEGA SATURN in usbhid.conf
- Added omxplayer to enable Introduction video
- Updated recalbox-configgen to version 4.1.X
- Added linapple-pie to recalbox-rpi3_defconfig
- Added support for vice 2.4.24. This means support for commodore c64 and other commodore systems
- Added theme for commodore c64
- Added two demo ROMs for commodore c64
- Add linapple specific parameters to start fixing an issue.
- Added user's configuration files upgrade
- Merged buildroot upstream
- Added retroachievements hardcore mode
- Add omxplayer to rpi2 & rpi3 defconfig
- Add Kodi default plugins/repositories
- Improved S02splash script for video splash
- linapple-pie download redirected to LaurentMarchelli
- passed to gcc5
- Added pgrep to busybox for omxplayer extensions
- New video version and splash video now stopped when kodi is started
- Added custom ratio per game option
- Dbus implementation to have fade out effect on splash video
- Added Witty Pi powerswitch support with Wiring Pi.
- Network connection manager : ethernet configuration on wire connection
- Network connection manager : multiple wifi configurations
- Wifi : open/wep/wpa/wpa2
- New emulator : reicast
- Bumped retroarch to v1.3.4
- Added retroachievements support to fceunext core
- Reicast : add multiplayer support
- Update to moonlight-embedded-2.2.1 (but still displays 2.2.0 when running), adds support for GFE 2.11
- Added enet library for moonlight-embedded-2.2.0
- Solved a bug on xarcade where B and HOTKEY were sending the same event
- Slide transition by default in ES
- Power management switch support (power,reset and LED) for pin 3/5/6
- Add ifconfig -a and /boot/recalbox-boot.conf in recalbox-support.sh
- S99Custom now trasmits its init parameter to custom.sh
- Add ipega 9021 rules
- ES now shutdowns the system
- share/roms/saves/bios available via a network point
- bumped SDL to 2.0.4
- disable multitouch axis in SDL 2.0.4
- linux kernel bumped to 4.4.13
- Add new Traditional Chinese Language
- Add DosBox 0.74 (rev 3989) with specific patches: SDL2, with mapping of mouse and all axis of joysticks
- Add lutro extension

## [4.0.0-beta3] - 2016-04-19
- Xarcade2jstick button remapped + better support of IPAC encoders
- Added IPAC2 keyboard encoder
- Patched xpad driver to support Xbox One controllers in USB mode
- Updated gamepads inputs to support moonlight
- Fix some kodi bugs about joysticks
- Added OpenGL + scalers supports to scummvm
- Power management switch support for pin 5/6
- Fix freeze issue with libretro-mgba core
- Added megatools
- Added new recalbox 4.0.0 systems
- Added crt-pi shaders
- Fix Namco/Taito games in mame2003
- Added kempston joystick by default for zxspectrum
- Updated scummvm to version 1.8
- Added VIM
- Added recalbox-themes package
- Recalbox theme by default

## [4.0.0-beta2]
- Added rpi3 support (without bluetooth)
- Added support for power management boards
- Added rpi gpio and wiringpi
- Added OOB remote controls
- Fixed keyboard issue in ES
- Fixed retroachievement support on picodrive and fceumm libretro cores
- Fixed system locales
- Updated 8bitdo gamepads
- Bumped to moonlight-embedded-2.1.4
- Overclock set to none now delete lines in config.txt 
- Improved keyboard encoders support
- Fixed an issue concerning ISO loading taking too long

## [4.0.0-beta1]
- new update process
- new languages
- external storage choice
- favourite system

## [3.3.0-beta17]
- New version of xboxdrv
- Corrected 8bitdo mapping
- Added wiringpi
- switch USBHID to kernel module for gamepad encoders
- linapple-pie (Apple ][ Emulator) added to rpi2, rpi1 need to be tested

## [3.3.0-beta16] - 2015-11-24
- Corrected kodi start
- Bumped to moonlight-embedded-2.1.2

## [3.3.0-beta15] - 2015-11-22
- Corrected sound issues with IREM games on libretro-mame2003 core
- Updated libretro-fba core from FBA 0.2.97.36 to FBA 0.2.97.37
- Added recalbox api
- Added Chinese and Turkish
- Added samba switch in recalbox.conf
- Added WiiMote support
- Added Kodi controller support 
- Corrected controller <-> player attribution
- Added moonlight system support, with roms
- Added new switch in recalbox.conf for ssh and virtual gamepads

## [3.3.0-beta14] - 2015-11-01
- Corrected recalbox manager

## [3.3.0-beta13] - 2015-11-01
- Added recalbox-manager
- Added custom ratio support

## [3.3.0-beta12] - 2015-10-31
- Added EmulationStation shutdown screen
- Corrected select to quit shortcut

## [3.3.0-beta11] - 2015-10-31
- Corrected shadersets bug

## [3.3.0-beta10] - 2015-10-31
- Added GLideN64 video plugin
- Added mame2003 libretro as default mame emulator
- Added system.emulators.specialkeys to select the emulators special keys functions
- Updated snes9x core (fix the bomberman 5 freeze)
- Added Saitek controllers support
- Added select shortcut in menu for quick restart / shutdown
- Added Basque language

## [3.3.0-beta9] - 2015-10-11
- Fixed Moonlight theme for zoid
- Added splashscreen for long reboots
- Added mplayer and jscal 
- Updated atari 2600 stella core for 2 players support
- Updated fba libretro for R3 diag menu
- Added xbox 360 official wireless dongle support OOTB
- Added fullscreen/ratio/widescreen hack settings for n64

## [3.3.0-beta8] - 2015-10-06
- Removed avahi daemon
- Fixed Moonlight theme

## [3.3.0-beta7] - 2015-09-20
- Updated themes + added moonlight themes
- Updated .dat and infos about fba_libretro romset
- Updated recalbox.conf with list of cores not supporting rewind
- Added system.es.menu option
- Added Moonlight
- Added kodi webserver on port 8081
- Added auto-connection for bluetooth controllers

## [3.3.0-beta6] - 2015-09-15
- More 8bitdo support
- Corrected retro shaderset for mastersystem
- Corrected kodi autostart

## [3.3.0-beta5] - 2015-09-13
- Added scanlines and retro shadersets
- Added name based sdl2 driver switch (8bitdo support)
- Added cavestory support
- Added mad and vorbis support in scummvm
- Refactored ES recalbox.conf management

## [3.3.0-beta4] - 2015-09-05
- Corrected start kodi with X
- Added NES30 Pro Support
- Added SFC30 Support
- Ignore cheats for updates

## [3.3.0-beta3] - 2015-08-29
- Added xiaomi bluetooth controller config
- Added default videomode that doesn't change the resolution while launching games
- Added 16/10 support and 16/10 is set as default for wswan
- Added recalbox version of Virtual Gamepad
- Added retroarch input driver autoconfig based on guid
- Added doom 1 shareware

## [3.3.0-beta2] - 2015-08-23
- Changed update repo and system

## [3.3.0-beta1] - 2015-08-22
- Added Wonderswan Color libretro emulator
- Added Lutro libretro core (LUA framework)
- Added NeoGeo as a separated system
- Added NeoGeo Pocket Color libretro emulator
- Added Vectrex libretro emulator
- Added Game And Watch libretro emulator
- Added Lynx libretro emulator
- Added PRBoom libretro 
- Modif zoid theme
- Patched kernel to support retrobit controllers
- Patched kernel to support 4NES4SNES controllers
- Patched kernel to fix the blinking xbox led. Only on rpi2
- Added gpu_mem for 256mo rpi1
- Unified the branches rpi and rpi2
- Updated buildroot sources
- Added libretro cheats
- Added favorites to emulationstation (from kaptainkia es modifications)
- Added mk_arcade_joystick_rpi with one more button
- Added adafruit-retrogame utility
- Added recalbox-configgen support
- Added sixad driver choice
- Added SuperGrafx libretro emulator
- Added NXengine libretro core (cavestory)
- Added Atari 7800 libretro emulator
- Added hostname in recalbox.conf
- Added recalbox-system (recalbox.arch file)
- Changed bash as default shell
- Corrected update system
- Added Tgbdual libretro core
- Added Miroof's Virtual Gamepads
- Added silent install
 
## [3.2.11] - 2015-03-24
- Corrected issues with controllers with idientical names
- Added zoid theme

## [3.2.10] - 2015-03-17
- Corrected itialian translation
- Recompiled modules for 3.19

## [3.2.9] - 2015-03-15
### Changed
- Added fba emulator switch
- Added snes9x, catsfc, pocketsnes switch 
- Added virtualboy platform
- Fixed : buttons on axis in retroarch config
- Added timestamps in logs
- Fixed xboxdrv pacakge
- Bumbep to Kodi-14.2-rc1
- Added clrmame info and dat files for mame and fba
- Added fbalibretro system
- Added italian translation

## [3.2.8] - 2015-03-09
### Changed
- Added switches in recalbox.conf
    - kodi x button switch
    - game resolution switch
    - update check switch
    - xboxdrv switch
    - localtime switch
- Fixed : mupen rice plugin package
- Fixed : xboxdrv pacakge
- Added localtime support
- Added mgd extension for snes
- Fixed : L2 + R2 mapping in retroarch
- Fixed : only axis based joystick configuration
- Changed all package to specific versions
- Bumped to 3.19 for rpi2
- Bumped to last userland and firmware
- Kodi PVR support
- Added cifs support
- Added ipv6 support
- Fixed : hats for specials key on retroarch

## [3.2.7] - 2015-03-03
- Fixed boot process

## [3.2.6] - 2015-03-03
### Changed
- Added z64 extenson for n64
- Added xbox360 wireless defaut configuration
- Fixed : power management of ew-7811un
- Added kodi mysql support
- Fixed nfs startup script

## [3.2.5] - 2015-03-03
### Changed
- Added samba socket option for large files copy
- Added db9 driver package
- Added gamecon driver package
- Added new setting configuration file (recalbox.conf)
- Added new startup system
- Fixed : ssid with space from emulationstation
- Fixed : ntfs automount
