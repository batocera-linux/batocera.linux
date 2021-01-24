################################################################################
#
# DUCKSTATION
#
################################################################################
# Version.: Commits on Jan 21, 2021
DUCKSTATION_VERSION = 443319766523e6396abe52a8e1721146e3943896
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
else
DUCKSTATION_CONF_OPTS += -DBUILD_QT_FRONTEND=OFF -DBUILD_SDL_FRONTEND=ON -DUSE_EGL=ON -DUSE_WAYLAND=OFF -DUSE_X11=OFF
DUCKSTATION_DEPENDENCIES += libegl sdl2
DUCKSTATION_CONF_OPTS += -DCMAKE_C_FLAGS="-DEGL_NO_X11"
DUCKSTATION_CONF_OPTS += -DCMAKE_CXX_FLAGS="-DEGL_NO_X11"
endif

DUCKSTATION_CONF_ENV += LDFLAGS=-lpthread

# Should be set when the package cannot be built inside the source tree but needs a separate build directory.
DUCKSTATION_SUPPORTS_IN_SOURCE_BUILD = NO

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_X86_64),y)
define DUCKSTATION_INSTALL_TARGET_CMDS
        mkdir -p $(TARGET_DIR)/usr/bin
        mkdir -p $(TARGET_DIR)/usr/lib
        mkdir -p $(TARGET_DIR)/usr/share/duckstation

	$(INSTALL) -D $(@D)/buildroot-build/bin/duckstation-qt \
		$(TARGET_DIR)/usr/bin/
	cp -R $(@D)/buildroot-build/bin/database      $(TARGET_DIR)/usr/share/duckstation/
	cp -R $(@D)/buildroot-build/bin/inputprofiles $(TARGET_DIR)/usr/share/duckstation/
	cp -R $(@D)/buildroot-build/bin/shaders       $(TARGET_DIR)/usr/share/duckstation/
	cp -R $(@D)/buildroot-build/bin/translations  $(TARGET_DIR)/usr/share/duckstation/
endef
else
define DUCKSTATION_INSTALL_TARGET_CMDS
        mkdir -p $(TARGET_DIR)/usr/bin
        mkdir -p $(TARGET_DIR)/usr/lib

	$(INSTALL) -D $(@D)/buildroot-build/bin/duckstation-sdl \
		$(TARGET_DIR)/usr/bin/
endef
endif

$(eval $(cmake-package))
