################################################################################
#
# catacombgl
#
################################################################################

CATACOMBGL_VERSION = 6c58d1fd17180deffee22220886858baa5f44d08
CATACOMBGL_SITE = $(call github,ArnoAnsems,CatacombGL,$(CATACOMBGL_VERSION))
CATACOMBGL_LICENSE = GPLv3
CATACOMBGL_LICENSE_FILES = COPYING.txt
CATACOMBGL_SUPPORTS_IN_SOURCE_BUILD = NO

CATACOMBGL_DEPENDENCIES = sdl2

define CATACOMBGL_EVMAPY
	mkdir -p $(TARGET_DIR)/usr/share/evmapy
	cp -prn $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/ports/catacombgl/catacomb.keys \
		$(TARGET_DIR)/usr/share/evmapy
endef

CATACOMBGL_POST_INSTALL_TARGET_HOOKS = CATACOMBGL_EVMAPY

$(eval $(cmake-package))
