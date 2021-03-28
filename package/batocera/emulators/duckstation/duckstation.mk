################################################################################
#
# DUCKSTATION
#
################################################################################
# Version.: Commits on Mar 28, 2021
DUCKSTATION_VERSION = ddea2818d94b32837f0d7ad33535c7290ee23ef8
DUCKSTATION_SITE = https://github.com/stenzek/duckstation.git

DUCKSTATION_DEPENDENCIES = fmt boost ffmpeg
DUCKSTATION_SITE_METHOD=git
DUCKSTATION_GIT_SUBMODULES=YES
DUCKSTATION_LICENSE = GPLv2

DUCKSTATION_CONF_OPTS  = -DENABLE_DISCORD_PRESENCE=OFF -DANDROID=OFF -DBUILD_LIBRETRO_CORE=OFF
DUCKSTATION_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release
DUCKSTATION_CONF_OPTS += -DBUILD_SHARED_LIBS=FALSE

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_X86_64),y)
DUCKSTATION_CONF_OPTS += -DBUILD_QT_FRONTEND=ON -DBUILD_SDL_FRONTEND=OFF -DUSE_WAYLAND=OFF -DUSE_X11=ON -DUSE_GLX=ON -DUSE_EGL=OFF
DUCKSTATION_DEPENDENCIES += qt5base qt5tools qt5multimedia
DUCKSTATION_BINARY = duckstation-qt
else
DUCKSTATION_CONF_OPTS += -DBUILD_QT_FRONTEND=OFF -DBUILD_SDL_FRONTEND=OFF -DBUILD_NOGUI_FRONTEND=ON -DUSE_DRMKMS=ON -DUSE_WAYLAND=OFF -DUSE_X11=OFF
DUCKSTATION_CONF_OPTS += -DCMAKE_C_FLAGS="-DEGL_NO_X11"
DUCKSTATION_DEPENDENCIES += libdrm sdl2 libevdev
DUCKSTATION_BINARY = duckstation-nogui
endif

ifeq ($(BR2_PACKAGE_HAS_LIBEGL),y)
DUCKSTATION_CONF_OPTS += -DUSE_EGL=ON
ifeq ($(BR2_PACKAGE_HAS_LIBMALI),y)
DUCKSTATION_CONF_OPTS += -DUSE_MALI=ON
endif
else
DUCKSTATION_CONF_OPTS += -DUSE_EGL=OFF
endif

DUCKSTATION_CONF_ENV += LDFLAGS=-lpthread


# Should be set when the package cannot be built inside the source tree but needs a separate build directory.
DUCKSTATION_SUPPORTS_IN_SOURCE_BUILD = NO

define DUCKSTATION_INSTALL_TARGET_CMDS
        mkdir -p $(TARGET_DIR)/usr/bin
        mkdir -p $(TARGET_DIR)/usr/lib
        mkdir -p $(TARGET_DIR)/usr/share/duckstation

	$(INSTALL) -D $(@D)/buildroot-build/bin/$(DUCKSTATION_BINARY) \
		$(TARGET_DIR)/usr/bin/duckstation
	cp -R $(@D)/buildroot-build/bin/database      $(TARGET_DIR)/usr/share/duckstation/
	rm -f $(TARGET_DIR)/usr/share/duckstation/database/gamecontrollerdb.txt
	cp -R $(@D)/buildroot-build/bin/inputprofiles $(TARGET_DIR)/usr/share/duckstation/
	cp -R $(@D)/buildroot-build/bin/resources     $(TARGET_DIR)/usr/share/duckstation/
	cp -R $(@D)/buildroot-build/bin/shaders       $(TARGET_DIR)/usr/share/duckstation/
endef

define DUCKSTATION_EVMAPY
	mkdir -p $(TARGET_DIR)/usr/share/evmapy
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulators/duckstation/psx.duckstation.keys $(TARGET_DIR)/usr/share/evmapy
endef

define DUCKSTATION_TRANSLATIONS
	mkdir -p $(TARGET_DIR)/usr/share/duckstation
	cp -R $(@D)/buildroot-build/bin/translations  $(TARGET_DIR)/usr/share/duckstation/
endef

DUCKSTATION_POST_INSTALL_TARGET_HOOKS += DUCKSTATION_EVMAPY
ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_X86_64),y)
DUCKSTATION_POST_INSTALL_TARGET_HOOKS += DUCKSTATION_TRANSLATIONS
endif

$(eval $(cmake-package))
