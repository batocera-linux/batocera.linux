################################################################################
#
# DOLPHIN EMU
#
################################################################################
# Version: Commits on Nov 14, 2021 - 5.0-15478
DOLPHIN_EMU_VERSION = a58b1dc38b9825dea29da15389b765a4e6ddaa6c
DOLPHIN_EMU_SITE = $(call github,dolphin-emu,dolphin,$(DOLPHIN_EMU_VERSION))
DOLPHIN_EMU_LICENSE = GPLv2+
DOLPHIN_EMU_DEPENDENCIES = libevdev ffmpeg zlib libpng lzo libusb libcurl bluez5_utils hidapi xz host-xz

DOLPHIN_EMU_SUPPORTS_IN_SOURCE_BUILD = NO

DOLPHIN_EMU_CONF_OPTS  = -DTHREADS_PTHREAD_ARG=OFF
DOLPHIN_EMU_CONF_OPTS += -DUSE_DISCORD_PRESENCE=OFF
DOLPHIN_EMU_CONF_OPTS += -DBUILD_SHARED_LIBS=OFF
DOLPHIN_EMU_CONF_OPTS += -DDISTRIBUTOR='batocera.linux'

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_X86_64),y)
DOLPHIN_EMU_DEPENDENCIES += xserver_xorg-server qt5base
DOLPHIN_EMU_CONF_OPTS += -DENABLE_NOGUI=OFF
DOLPHIN_EMU_CONF_OPTS += -DENABLE_EGL=OFF
endif

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_S922X),y)
DOLPHIN_EMU_DEPENDENCIES += libdrm
DOLPHIN_EMU_CONF_OPTS += -DENABLE_QT=OFF
DOLPHIN_EMU_CONF_OPTS += -DENABLE_EGL=ON
DOLPHIN_EMU_CONF_OPTS += -DENABLE_LTO=ON
endif

ifeq ($(BR2_PACKAGE_BATOCERA_PANFROST_MESA3D),y)
DOLPHIN_EMU_CONF_OPTS += -DENABLE_VULKAN=ON
endif

$(eval $(cmake-package))
