################################################################################
#
# duckstation
#
################################################################################
# Version.: Commits on Jan 11, 2022
DUCKSTATION_VERSION = 51041e47f70123eda41d999701f5651830a0a95e
DUCKSTATION_SITE = https://github.com/stenzek/duckstation.git
DUCKSTATION_SITE_METHOD=git
DUCKSTATION_GIT_SUBMODULES=YES
DUCKSTATION_LICENSE = GPLv2
DUCKSTATION_DEPENDENCIES = fmt boost ffmpeg libcurl
DUCKSTATION_SUPPORTS_IN_SOURCE_BUILD = NO

DUCKSTATION_CONF_OPTS  = -DENABLE_DISCORD_PRESENCE=OFF -DANDROID=OFF -DBUILD_LIBRETRO_CORE=OFF \
                         -DCMAKE_BUILD_TYPE=Release -DBUILD_SHARED_LIBS=FALSE

DUCKSTATION_CONF_ENV += LDFLAGS=-lpthread

ifeq ($(BR2_PACKAGE_XORG7),y)
  DUCKSTATION_CONF_OPTS += -DUSE_X11=ON
else
  DUCKSTATION_CONF_OPTS += -DUSE_X11=OFF
endif

ifeq ($(BR2_PACKAGE_QT5),y)
  DUCKSTATION_CONF_OPTS += -DBUILD_QT_FRONTEND=ON -DBUILD_SDL_FRONTEND=OFF
  DUCKSTATION_DEPENDENCIES += qt5base qt5tools qt5multimedia
else
  DUCKSTATION_CONF_OPTS += -DBUILD_QT_FRONTEND=OFF -DBUILD_SDL_FRONTEND=OFF -DBUILD_NOGUI_FRONTEND=ON
  DUCKSTATION_DEPENDENCIES += libdrm sdl2 libevdev
endif

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_X86_64),y)
  DUCKSTATION_CONF_OPTS += -DUSE_WAYLAND=OFF -DUSE_GLX=ON
else
  DUCKSTATION_CONF_OPTS += -DUSE_DRMKMS=ON -DUSE_WAYLAND=OFF -DUSE_GBM=ON
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
  cp -R $(@D)/buildroot-build/bin/database      $(TARGET_DIR)/usr/share/duckstation/
  rm -f $(TARGET_DIR)/usr/share/duckstation/database/gamecontrollerdb.txt
  cp -R $(@D)/buildroot-build/bin/inputprofiles $(TARGET_DIR)/usr/share/duckstation/
  cp -R $(@D)/buildroot-build/bin/resources     $(TARGET_DIR)/usr/share/duckstation/
  cp -R $(@D)/buildroot-build/bin/shaders       $(TARGET_DIR)/usr/share/duckstation/

  mkdir -p $(TARGET_DIR)/usr/share/evmapy
  cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulators/duckstation/psx.duckstation.keys $(TARGET_DIR)/usr/share/evmapy
endef

define DUCKSTATION_TRANSLATIONS
  mkdir -p $(TARGET_DIR)/usr/share/duckstation
  cp -R $(@D)/buildroot-build/bin/translations  $(TARGET_DIR)/usr/share/duckstation/
endef

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_X86_64),y)
  DUCKSTATION_POST_INSTALL_TARGET_HOOKS += DUCKSTATION_TRANSLATIONS
endif

$(eval $(cmake-package))
