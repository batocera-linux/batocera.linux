################################################################################
#
# dolphin-emu
#
################################################################################

# version - 5.0-16377 - Commits on May 4, 2022
DOLPHIN_EMU_VERSION = d0ed09ab6fe8e19a64e8f1bb2867f9c439616d4c
DOLPHIN_EMU_SITE = $(call github,dolphin-emu,dolphin,$(DOLPHIN_EMU_VERSION))
DOLPHIN_EMU_LICENSE = GPLv2+
DOLPHIN_EMU_DEPENDENCIES = libevdev ffmpeg zlib libpng lzo libusb libcurl bluez5_utils hidapi xz host-xz
DOLPHIN_EMU_SUPPORTS_IN_SOURCE_BUILD = NO

DOLPHIN_EMU_CONF_OPTS  = -DTHREADS_PTHREAD_ARG=OFF
DOLPHIN_EMU_CONF_OPTS += -DUSE_DISCORD_PRESENCE=OFF
DOLPHIN_EMU_CONF_OPTS += -DBUILD_SHARED_LIBS=OFF
DOLPHIN_EMU_CONF_OPTS += -DDISTRIBUTOR='batocera.linux'
DOLPHIN_EMU_CONF_OPTS += -DUSE_MGBA=OFF

ifeq ($(BR2_PACKAGE_XSERVER_XORG_SERVER),y)
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

ifeq ($(BR2_PACKAGE_BATOCERA_PANFROST_MESA3D)$(BR2_PACKAGE_BATOCERA_TARGET_X86_64),y)
DOLPHIN_EMU_CONF_OPTS += -DENABLE_VULKAN=ON
endif

define DOLPHIN_EMU_EVMAPY
	mkdir -p $(TARGET_DIR)/usr/share/evmapy
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulators/dolphin-emu/*.keys $(TARGET_DIR)/usr/share/evmapy
endef

DOLPHIN_EMU_POST_INSTALL_TARGET_HOOKS = DOLPHIN_EMU_EVMAPY

$(eval $(cmake-package))
