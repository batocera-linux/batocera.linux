################################################################################
#
# flycast
#
################################################################################
# Version: Commits on Jul 30, 2024
FLYCAST_VERSION = 45bf218df428123f739714ef4e65e1b96c0959b7
FLYCAST_SITE = https://github.com/flyinghead/flycast.git
FLYCAST_SITE_METHOD=git
FLYCAST_GIT_SUBMODULES=YES
FLYCAST_LICENSE = GPLv2
FLYCAST_DEPENDENCIES = boost sdl2 libpng libzip libcurl libao libminiupnpc elfutils

FLYCAST_SUPPORTS_IN_SOURCE_BUILD = NO

FLYCAST_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release
FLYCAST_CONF_OPTS += -DBUILD_SHARED_LIBS=OFF
FLYCAST_CONF_OPTS += -DLIBRETRO=OFF
FLYCAST_CONF_OPTS += -DUSE_HOST_SDL=ON
FLYCAST_CONF_OPTS += -DUSE_DX9=OFF
FLYCAST_CONF_OPTS += -DUSE_DX11=OFF

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_X86_64_ANY),y)
    FLYCAST_CONF_OPTS += -DUSE_OPENGL=ON
else ifeq ($(BR2_PACKAGE_BATOCERA_GLES3),y)
    FLYCAST_CONF_OPTS += -DUSE_GLES=ON -DUSE_GLES2=OFF -DUSE_OPENGL=ON
else ifeq ($(BR2_PACKAGE_BATOCERA_GLES2),y)
    FLYCAST_CONF_OPTS += -DUSE_GLES2=ON -DUSE_GLES=OFF -DUSE_OPENGL=ON
endif

ifeq ($(BR2_PACKAGE_BATOCERA_VULKAN),y)
    FLYCAST_CONF_OPTS += -DUSE_VULKAN=ON
else
    FLYCAST_CONF_OPTS += -DUSE_VULKAN=OFF
endif

# RPI: use the legacy Broadcom GLES libraries
ifeq ($(BR2_PACKAGE_BATOCERA_RPI_VCORE),y)
    FLYCAST_CONF_OPTS += -DUSE_VIDEOCORE=ON
endif

ifeq ($(BR2_PACKAGE_HAS_LIBMALI),y)
    FLYCAST_DEPENDENCIES += libmali
    FLYCAST_CONF_OPTS += -DUSE_MALI=ON
endif

define FLYCAST_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/buildroot-build/flycast $(TARGET_DIR)/usr/bin/flycast
	# evmapy files
	mkdir -p $(TARGET_DIR)/usr/share/evmapy
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulators/flycast/*.keys \
        $(TARGET_DIR)/usr/share/evmapy
endef

$(eval $(cmake-package))
