################################################################################
#
# duckstation
#
################################################################################
# Version: Commits on Feb 25, 2024
DUCKSTATION_VERSION = 4a70164daca18ecf86873b02cd9677e696d18d62
DUCKSTATION_SITE = https://github.com/stenzek/duckstation.git
DUCKSTATION_SITE_METHOD=git
DUCKSTATION_GIT_SUBMODULES=YES
DUCKSTATION_LICENSE = GPLv2
DUCKSTATION_DEPENDENCIES = fmt boost ffmpeg libcurl ecm

DUCKSTATION_SUPPORTS_IN_SOURCE_BUILD = NO

DUCKSTATION_CONF_OPTS  = -DCMAKE_BUILD_TYPE=Release
DUCKSTATION_CONF_OPTS += -DBUILD_SHARED_LIBS=FALSE
DUCKSTATION_CONF_OPTS += -DENABLE_DISCORD_PRESENCE=OFF

DUCKSTATION_CONF_ENV += LDFLAGS=-lpthread

ifeq ($(BR2_PACKAGE_WAYLAND),y)
    DUCKSTATION_CONF_OPTS += -DENABLE_WAYLAND=ON
else
    DUCKSTATION_CONF_OPTS += -DENABLE_WAYLAND=OFF
endif

ifeq ($(BR2_PACKAGE_XORG7),y)
    DUCKSTATION_CONF_OPTS += -DENABLE_X11=ON
else
    DUCKSTATION_CONF_OPTS += -DENABLE_X11=OFF
endif

ifeq ($(BR2_PACKAGE_VULKAN_HEADERS)$(BR2_PACKAGE_VULKAN_LOADER),yy)
    DUCKSTATION_CONF_OPTS += -DENABLE_VULKAN=ON
else
    DUCKSTATION_CONF_OPTS += -DENABLE_VULKAN=OFF
endif

# QT6 under wayland is failing currently
ifeq ($(BR2_PACKAGE_QT6)$(BR2_PACKAGE_XORG7),yy)
    DUCKSTATION_CONF_OPTS += -DBUILD_QT_FRONTEND=ON
    DUCKSTATION_DEPENDENCIES += qt6base qt6tools qt6svg
else
    DUCKSTATION_CONF_OPTS += -DBUILD_QT_FRONTEND=OFF
    DUCKSTATION_CONF_OPTS += -DBUILD_NOGUI_FRONTEND=ON
    DUCKSTATION_DEPENDENCIES += libdrm sdl2 libevdev libxkbcommon
endif

define DUCKSTATION_INSTALL_TARGET_CMDS
    mkdir -p $(TARGET_DIR)/usr/bin
    mkdir -p $(TARGET_DIR)/usr/lib
    mkdir -p $(TARGET_DIR)/usr/share/duckstation

    $(INSTALL) -D $(@D)/buildroot-build/bin/duckstation* \
        $(TARGET_DIR)/usr/bin/
    cp -R $(@D)/buildroot-build/bin/resources \
        $(TARGET_DIR)/usr/share/duckstation/
    rm -f $(TARGET_DIR)/usr/share/duckstation/resources/gamecontrollerdb.txt

    mkdir -p $(TARGET_DIR)/usr/share/evmapy
    cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulators/duckstation/psx.duckstation.keys \
        $(TARGET_DIR)/usr/share/evmapy
endef

define DUCKSTATION_TRANSLATIONS
    mkdir -p $(TARGET_DIR)/usr/share/duckstation
    cp -R $(@D)/buildroot-build/bin/translations \
        $(TARGET_DIR)/usr/share/duckstation/
endef

ifeq ($(BR2_PACKAGE_QT6)$(BR2_PACKAGE_XORG7),yy)
    DUCKSTATION_POST_INSTALL_TARGET_HOOKS += DUCKSTATION_TRANSLATIONS
endif

$(eval $(cmake-package))
