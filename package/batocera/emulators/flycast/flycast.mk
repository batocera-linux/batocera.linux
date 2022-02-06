################################################################################
#
# flycast
#
################################################################################

# version: Commits on Dec 19, 2021
# don't go beyond this until SDL is upgraded
FLYCAST_VERSION = e706368225d7c9a77713e6ee6614616401745cf0
FLYCAST_SITE = https://github.com/flyinghead/flycast.git
FLYCAST_SITE_METHOD=git
FLYCAST_GIT_SUBMODULES=YES
FLYCAST_LICENSE = GPLv2
FLYCAST_DEPENDENCIES = sdl2 libpng libzip libao pulseaudio-utils

FLYCAST_CONF_OPTS += -DLIBRETRO=OFF

# determine the best GLES version to use - prefer GLES3
ifeq ($(BR2_PACKAGE_BATOCERA_GLES3),y)
    FLYCAST_CONF_OPTS += -DUSE_GLES=ON -DUSE_GLES2=OFF
else ifeq ($(BR2_PACKAGE_BATOCERA_GLES2),y)
    FLYCAST_CONF_OPTS += -DUSE_GLES2=ON -DUSE_GLES=OFF
endif

ifeq ($(BR2_PACKAGE_BATOCERA_VULKAN),y)
    FLYCAST_CONF_OPTS += -DUSE_VULKAN=ON
else
    FLYCAST_CONF_OPTS += -DUSE_VULKAN=OFF
endif

# RPI: use the legacy Broadcom GLES libraries
ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI2)$(BR2_PACKAGE_BATOCERA_TARGET_RPIZERO2),y)
    FLYCAST_CONF_OPTS += -DUSE_VIDEOCORE
endif

ifeq ($(BR2_PACKAGE_HAS_LIBMALI),y)
    FLYCAST_CONF_OPTS += EXTRAFLAGS=-Wl,-lmali
endif

define FLYCAST_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/flycast $(TARGET_DIR)/usr/bin/flycast
	# evmapy files
	mkdir -p $(TARGET_DIR)/usr/share/evmapy
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulators/flycast/*.keys $(TARGET_DIR)/usr/share/evmapy
endef

$(eval $(cmake-package))
