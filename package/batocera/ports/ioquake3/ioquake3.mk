################################################################################
#
# ioquake3
#
################################################################################
# Version: Commits on Jul 6, 2023
IOQUAKE3_VERSION = 10a45cbdc131a35530d89bd3cfc2a7eed74b54cc
IOQUAKE3_SITE = $(call github,ioquake,ioq3,$(IOQUAKE3_VERSION))
IOQUAKE3_LICENSE = GPL-2.0
IOQUAKE3_LICENSE_FILE = COPYING.txt

IOQUAKE3_DEPENDENCIES = sdl2

IOQUAKE3_BUILD_ARGS += BUILD_SERVER=0
IOQUAKE3_BUILD_ARGS += BUILD_CLIENT=1
IOQUAKE3_BUILD_ARGS += BUILD_BASEGAME=1
IOQUAKE3_BUILD_ARGS += BUILD_MISSIONPACK=1
IOQUAKE3_BUILD_ARGS += BUILD_GAME_SO=0
IOQUAKE3_BUILD_ARGS += BUILD_GAME_QVM=0
IOQUAKE3_BUILD_ARGS += CROSS_COMPILING=1
IOQUAKE3_BUILD_ARGS += USE_RENDERER_DLOPEN=0

define IOQUAKE3_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" \
	    $(IOQUAKE3_BUILD_ARGS) -C $(@D) -f Makefile
endef

define IOQUAKE3_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/usr/bin/ioquake3
	$(INSTALL) -D $(@D)/build/release-linux-x86_64/ioquake3_opengl2.x86_64 \
		$(TARGET_DIR)/usr/bin/ioquake3/ioquake3
endef

define IOQUAKE3_EVMAPY
	mkdir -p $(TARGET_DIR)/usr/share/evmapy
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/ports/ioquake3/quake3.keys \
	    $(TARGET_DIR)/usr/share/evmapy
endef

IOQUAKE3_POST_INSTALL_TARGET_HOOKS += IOQUAKE3_EVMAPY

$(eval $(generic-package))
