################################################################################
#
# DOLPHIN EMU
#
################################################################################
# Version: Commits on Jul 5, 2020 (5.0-12257)
DOLPHIN_EMU_VERSION = 0dbe8fb2eaa608a6540df3d269648a596c29cf4b
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

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_ODROIDN2)$(BR2_PACKAGE_BATOCERA_TARGET_VIM3),y)
DOLPHIN_EMU_CONF_ENV += CFLAGS="-Ofast -march=armv8-a+crc+fp+simd+crypto -mcpu=cortex-a73.cortex-a53+crc+fp+simd+crypto -mtune=cortex-a73.cortex-a53 -ftree-vectorize -fwhole-program -flto=4 -mfloat-abi=hard -mfpu=crypto-neon-fp-armv8"
DOLPHIN_EMU_CONF_ENV += CXXFLAGS="${CFLAGS}"
DOLPHIN_EMU_CONF_ENV += LDFLAGS="${CXXFLAGS}"
endif

DOLPHIN_EMU_CONF_OPTS  = -DTHREADS_PTHREAD_ARG=OFF
DOLPHIN_EMU_CONF_OPTS += -DUSE_DISCORD_PRESENCE=OFF
DOLPHIN_EMU_CONF_OPTS += -DBUILD_SHARED_LIBS=OFF
DOLPHIN_EMU_CONF_OPTS += -DENABLE_EGL=OFF
DOLPHIN_EMU_CONF_OPTS += -DDISTRIBUTOR='batocera.linux'

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_ODROIDN2)$(BR2_PACKAGE_BATOCERA_TARGET_VIM3),y)
DOLPHIN_EMU_CONF_OPTS += -DENABLE_EGL=ON
endif

$(eval $(cmake-package))
