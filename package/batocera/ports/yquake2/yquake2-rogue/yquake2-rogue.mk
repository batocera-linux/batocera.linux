################################################################################
#
# yquake2-rogue
#
################################################################################

YQUAKE2_ROGUE_VERSION = ROGUE_2_15
YQUAKE2_ROGUE_SITE = $(call github,yquake2,rogue,$(YQUAKE2_ROGUE_VERSION))
YQUAKE2_ROGUE_LICENSE = GPLv2
YQUAKE2_ROGUE_LICENSE_FILES = LICENSE

YQUAKE2_ROGUE_DEPENDENCIES += yquake2

YQUAKE2_ROGUE_BUILD_ARGS = YQ2_OSTYPE=Linux

ifeq ($(BR2_aarch64),y)
    YQUAKE2_ROGUE_BUILD_ARGS += YQ2_ARCH=aarch64
else ifeq ($(BR2_arm),y)
    YQUAKE2_ROGUE_BUILD_ARGS += YQ2_ARCH=arm
else ifeq ($(BR2_x86_64),y)
    YQUAKE2_ROGUE_BUILD_ARGS += YQ2_ARCH=x86_64
else ifeq ($(BR2_i386),y)
    YQUAKE2_ROGUE_BUILD_ARGS += YQ2_ARCH=i386
endif

define YQUAKE2_ROGUE_BUILD_CMDS
    $(MAKE) $(TARGET_CONFIGURE_OPTS) $(YQUAKE2_ROGUE_BUILD_ARGS) -C $(@D)
endef

define YQUAKE2_ROGUE_INSTALL_TARGET_CMDS
    mkdir -p $(TARGET_DIR)/usr/bin/yquake2/rogue
    $(INSTALL) -D -m 0644 $(@D)/release/game.so \
        $(TARGET_DIR)/usr/bin/yquake2/rogue/
endef

$(eval $(generic-package))
