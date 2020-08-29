################################################################################
#
# LIBRETRO-DOLPHIN
#
################################################################################
# Version.: Commits on Aug 28, 2020
LIBRETRO_DOLPHIN_VERSION = b5ff41144d9f9df06246a617fc9a938c67527275
LIBRETRO_DOLPHIN_SITE = $(call github,libretro,dolphin,$(LIBRETRO_DOLPHIN_VERSION))
LIBRETRO_DOLPHIN_LICENSE = GPLv2

LIBRETRO_DOLPHIN_SUPPORTS_IN_SOURCE_BUILD = NO

LIBRETRO_DOLPHIN_CONF_OPTS  = -DLIBRETRO=ON
LIBRETRO_DOLPHIN_CONF_OPTS += -DLIBRETRO_STATIC=ON
LIBRETRO_DOLPHIN_CONF_OPTS += -DENABLE_NOGUI=OFF
LIBRETRO_DOLPHIN_CONF_OPTS += -DENABLE_QT=OFF
LIBRETRO_DOLPHIN_CONF_OPTS += -DENABLE_TESTS=OFF
LIBRETRO_DOLPHIN_CONF_OPTS += -DUSE_DISCORD_PRESENCE=OFF
LIBRETRO_DOLPHIN_CONF_OPTS += -DDISTRIBUTOR='batocera.linux'
LIBRETRO_DOLPHIN_CONF_OPTS += -DBUILD_SHARED_LIBS=OFF

#option(USE_SHARED_ENET "Use shared libenet if found rather than Dolphin's soon-to-compatibly-diverge version" OFF)
#option(USE_UPNP "Enables UPnP port mapping support" ON)
#option(ENABLE_LTO "Enables Link Time Optimization" OFF)
#option(ENABLE_GENERIC "Enables generic build that should run on any little-endian host" OFF)
#option(ENABLE_HEADLESS "Enables running Dolphin as a headless variant" OFF)
#option(ENABLE_ALSA "Enables ALSA sound backend" ON)
#option(ENABLE_PULSEAUDIO "Enables PulseAudio sound backend" ON)
#option(ENABLE_LLVM "Enables LLVM support, for disassembly" ON)

LIBRETRO_DOLPHIN_PLATFORM = $(LIBRETRO_PLATFORM)

$(eval $(cmake-package))
