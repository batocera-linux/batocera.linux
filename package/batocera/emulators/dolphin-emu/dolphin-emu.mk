################################################################################
#
# dolphin-emu
#
################################################################################

# Version: 5.0-19316 - Commits on Apr 29, 2023
DOLPHIN_EMU_VERSION = 8e6e6f3c4ac691f3db9c045945a61ecf271afdd7
DOLPHIN_EMU_SITE = https://github.com/dolphin-emu/dolphin
DOLPHIN_EMU_SITE_METHOD = git
DOLPHIN_EMU_LICENSE = GPLv2+
DOLPHIN_EMU_GIT_SUBMODULES = YES
DOLPHIN_EMU_SUPPORTS_IN_SOURCE_BUILD = NO

DOLPHIN_EMU_DEPENDENCIES = libevdev ffmpeg zlib libpng lzo libusb libcurl
DOLPHIN_EMU_DEPENDENCIES += bluez5_utils hidapi xz host-xz sdl2

DOLPHIN_EMU_CONF_OPTS  = -DCMAKE_BUILD_TYPE=Release
DOLPHIN_EMU_CONF_OPTS += -DBUILD_SHARED_LIBS=OFF
DOLPHIN_EMU_CONF_OPTS += -DDISTRIBUTOR='batocera.linux'
DOLPHIN_EMU_CONF_OPTS += -DUSE_DISCORD_PRESENCE=OFF
DOLPHIN_EMU_CONF_OPTS += -DUSE_MGBA=OFF
DOLPHIN_EMU_CONF_OPTS += -DUSE_UPNP=OFF
DOLPHIN_EMU_CONF_OPTS += -DENABLE_TESTS=OFF
DOLPHIN_EMU_CONF_OPTS += -DENABLE_AUTOUPDATE=OFF
DOLPHIN_EMU_CONF_OPTS += -DENABLE_ANALYTICS=OFF
# Disable QT until we fully support QT6, enable OpenGL as a result.
DOLPHIN_EMU_CONF_OPTS += -DENABLE_QT=OFF
DOLPHIN_EMU_CONF_OPTS += -DENABLE_EGL=ON

DOLPHIN_EMU_MAKE_ENV += LDFLAGS="-Wl,--copy-dt-needed-entries"
DOLPHIN_EMU_CONF_ENV += LDFLAGS="-Wl,--copy-dt-needed-entries"

ifeq ($(BR2_PACKAGE_XSERVER_XORG_SERVER),y)
    DOLPHIN_EMU_DEPENDENCIES += xserver_xorg-server
    DOLPHIN_EMU_CONF_OPTS += -DENABLE_X11=ON
else
    DOLPHIN_EMU_CONF_OPTS += -DENABLE_X11=OFF
endif

ifeq ($(BR2_PACKAGE_VULKAN_HEADERS)$(BR2_PACKAGE_VULKAN_LOADER),yy)
    DOLPHIN_EMU_CONF_OPTS += -DENABLE_VULKAN=ON
else
    DOLPHIN_EMU_CONF_OPTS += -DENABLE_VULKAN=OFF
endif

define DOLPHIN_EMU_EVMAPY
    mkdir -p $(TARGET_DIR)/usr/share/evmapy
    cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulators/dolphin-emu/*.keys \
        $(TARGET_DIR)/usr/share/evmapy
endef

$(eval $(cmake-package))
