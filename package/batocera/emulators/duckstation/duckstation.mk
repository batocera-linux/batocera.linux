################################################################################
#
# duckstation
#
################################################################################
# Version: Commits on May 2, 2023
DUCKSTATION_VERSION = 4cbb6e224787b5ae90b38d3cadffc4ccbe5754f0
DUCKSTATION_SITE = https://github.com/stenzek/duckstation.git
DUCKSTATION_SITE_METHOD=git
DUCKSTATION_GIT_SUBMODULES=YES
DUCKSTATION_LICENSE = GPLv2
DUCKSTATION_DEPENDENCIES = fmt boost ffmpeg libcurl ecm

DUCKSTATION_SUPPORTS_IN_SOURCE_BUILD = NO

DUCKSTATION_CONF_OPTS  = -DCMAKE_BUILD_TYPE=Release
DUCKSTATION_CONF_OPTS += -DBUILD_SHARED_LIBS=FALSE
DUCKSTATION_CONF_OPTS += -DENABLE_DISCORD_PRESENCE=OFF
DUCKSTATION_CONF_OPTS += -DUSE_DRMKMS=ON

DUCKSTATION_CONF_ENV += LDFLAGS=-lpthread

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RK3588),y)
  DUCKSTATION_CONF_OPTS += -DCMAKE_EXE_LINKER_FLAGS="-lmali_hook -Wl,--whole-archive -lmali_hook_injector -Wl,--no-whole-archive -lmali"
endif

ifeq ($(BR2_PACKAGE_WAYLAND),y)
    DUCKSTATION_CONF_OPTS += -DUSE_WAYLAND=ON
else
    DUCKSTATION_CONF_OPTS += -DUSE_WAYLAND=OFF
endif

ifeq ($(BR2_PACKAGE_XORG7),y)
    DUCKSTATION_CONF_OPTS += -DUSE_X11=ON
else
    DUCKSTATION_CONF_OPTS += -DUSE_X11=OFF
endif

ifeq ($(BR2_PACKAGE_VULKAN_HEADERS)$(BR2_PACKAGE_VULKAN_LOADER),yy)
    DUCKSTATION_CONF_OPTS += -DENABLE_VULKAN=ON
else
    DUCKSTATION_CONF_OPTS += -DENABLE_VULKAN=OFF
endif

ifeq ($(BR2_PACKAGE_QT6),y)
    DUCKSTATION_CONF_OPTS += -DBUILD_QT_FRONTEND=ON -DBUILD_SDL_FRONTEND=OFF
    DUCKSTATION_DEPENDENCIES += qt6base qt6tools qt6svg
else
    DUCKSTATION_CONF_OPTS += -DBUILD_QT_FRONTEND=OFF -DBUILD_SDL_FRONTEND=OFF -DBUILD_NOGUI_FRONTEND=ON
    DUCKSTATION_DEPENDENCIES += libdrm sdl2 libevdev
endif

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_X86_64_ANY),y)
    DUCKSTATION_CONF_OPTS += -DUSE_GLX=ON
endif

ifeq ($(BR2_PACKAGE_HAS_LIBEGL),y)
    DUCKSTATION_CONF_OPTS += -DUSE_EGL=ON
    ifeq ($(BR2_PACKAGE_HAS_LIBMALI),y)
        DUCKSTATION_CONF_OPTS += -DUSE_MALI=ON
    endif
else
    DUCKSTATION_CONF_OPTS += -DUSE_EGL=OFF
endif

define DUCKSTATION_INSTALL_TARGET_CMDS
    mkdir -p $(TARGET_DIR)/usr/bin
    mkdir -p $(TARGET_DIR)/usr/lib
    mkdir -p $(TARGET_DIR)/usr/share/duckstation

    $(INSTALL) -D $(@D)/buildroot-build/bin/duckstation* $(TARGET_DIR)/usr/bin/
    cp -R $(@D)/buildroot-build/bin/resources $(TARGET_DIR)/usr/share/duckstation/
    rm -f $(TARGET_DIR)/usr/share/duckstation/resources/gamecontrollerdb.txt

    mkdir -p $(TARGET_DIR)/usr/share/evmapy
    cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulators/duckstation/psx.duckstation.keys $(TARGET_DIR)/usr/share/evmapy
endef

define DUCKSTATION_TRANSLATIONS
    mkdir -p $(TARGET_DIR)/usr/share/duckstation
    cp -R $(@D)/buildroot-build/bin/translations  $(TARGET_DIR)/usr/share/duckstation/
endef

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_X86_64_ANY),y)
    DUCKSTATION_POST_INSTALL_TARGET_HOOKS += DUCKSTATION_TRANSLATIONS
endif

$(eval $(cmake-package))
