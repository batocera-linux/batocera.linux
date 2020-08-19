################################################################################
#
# DOLPHIN EMU
#
################################################################################
# Version: Commits on Jul 5, 2020 (5.0-12257)
DOLPHIN_EMU_VERSION = 905df6756b56ddfd7b4ead1f858c84f9e9608900
DOLPHIN_EMU_SITE = $(call github,dolphin-emu,dolphin,$(DOLPHIN_EMU_VERSION))
DOLPHIN_EMU_LICENSE = GPLv2+
DOLPHIN_EMU_DEPENDENCIES = libevdev ffmpeg zlib libpng lzo libusb libcurl bluez5_utils qt5base hidapi

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_X86_64),y)
DOLPHIN_EMU_DEPENDENCIES += xserver_xorg-server
endif
ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_ODROIDN2)$(BR2_PACKAGE_BATOCERA_TARGET_VIM3),y)
DOLPHIN_EMU_DEPENDENCIES += libdrm
endif

DOLPHIN_EMU_SUPPORTS_IN_SOURCE_BUILD = NO

DOLPHIN_EMU_CONF_OPTS  = -DTHREADS_PTHREAD_ARG=OFF
DOLPHIN_EMU_CONF_OPTS += -DUSE_DISCORD_PRESENCE=OFF
DOLPHIN_EMU_CONF_OPTS += -DBUILD_SHARED_LIBS=OFF
DOLPHIN_EMU_CONF_OPTS += -DENABLE_EGL=OFF
DOLPHIN_EMU_CONF_OPTS += -DDISTRIBUTOR='batocera.linux'

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_ODROIDN2)$(BR2_PACKAGE_BATOCERA_TARGET_VIM3),y)
DOLPHIN_EMU_CONF_OPTS += -DENABLE_EGL=ON
endif

$(eval $(cmake-package))
