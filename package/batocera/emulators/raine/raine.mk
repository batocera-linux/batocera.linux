################################################################################
#
# raine
#
################################################################################

RAINE_VERSION = 0.92.6
RAINE_SITE = $(call github,zelurker,raine,$(RAINE_VERSION))
RAINE_LICENSE = BSD
RAINE_DEPENDENCIES = sdl2 sdl2_net sdl2_image sdl2_ttf muparser

#RAINE_SITE_METHOD = git
#RAINE_GIT_SUBMODULES = YES

RAINE_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release
RAINE_CONF_OPTS += -DBUILD_SHARED_LIBS=ON
RAINE_CONF_OPTS += -DBUILD_TESTS=OFF
RAINE_CONF_OPTS += -DNO_ASM=1

define RAINE_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/usr/bin
	mkdir -p $(TARGET_DIR)/usr/lib

	$(INSTALL) -D $(@D)/raine \
		$(TARGET_DIR)/usr/bin/raine

	# evmap config
	mkdir -p $(TARGET_DIR)/usr/share/evmapy
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulators/raine/raine.keys $(TARGET_DIR)/usr/share/evmapy
endef

$(eval $(cmake-package))
