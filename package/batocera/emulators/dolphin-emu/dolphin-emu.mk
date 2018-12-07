################################################################################
#
# DOLPHIN EMU
#
################################################################################
# Version.: Commits on December 5, 2018
DOLPHIN_EMU_VERSION = 4e5f83d23fcee2e744890246360281639bf2ad18
DOLPHIN_EMU_SITE = $(call github,dolphin-emu,dolphin,$(DOLPHIN_EMU_VERSION))
DOLPHIN_EMU_DEPENDENCIES = xserver_xorg-server libevdev ffmpeg zlib libpng lzo libusb libcurl sfml bluez5_utils qt5base hidapi
DOLPHIN_EMU_SUPPORTS_IN_SOURCE_BUILD = NO

DOLPHIN_EMU_CONF_OPTS  = -DTHREADS_PTHREAD_ARG=OFF
DOLPHIN_EMU_CONF_OPTS += -DUSE_DISCORD_PRESENCE=OFF
DOLPHIN_EMU_CONF_OPTS += -DBUILD_SHARED_LIBS=OFF

$(eval $(cmake-package))
