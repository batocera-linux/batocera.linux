# Change Log
All notable changes to this project will be documented in this file.
This project adheres to [Semantic Versioning](http://semver.org/).

## [Unreleased][unreleased]

## [3.3.0-beta9] - 2015-10-XX
- Fixed Moonlight theme for zoid
- Added splashscreen for long reboots
- Added mplayer and jscal 
- Updated atari 2600 stella core for 2 players support
- Updated fba libretro for R3 diag menu
- Added xbox 360 official wireless dongle support OOTB
- Added gles2rice plugin for n64

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
