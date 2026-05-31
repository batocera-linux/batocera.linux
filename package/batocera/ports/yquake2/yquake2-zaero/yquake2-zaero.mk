################################################################################
#
# yquake2-zaero
#
################################################################################
# Version.: Commits on May 19, 2026
YQUAKE2_ZAERO_VERSION = fc5078830c1cb36c8ecd795cff1b761fc9feb971
YQUAKE2_ZAERO_SITE = $(call github,yquake2,zaero,$(YQUAKE2_ZAERO_VERSION))
YQUAKE2_ZAERO_LICENSE = Quake II SDK LICENSE
YQUAKE2_ZAERO_LICENSE_FILES = LICENSE

YQUAKE2_ZAERO_DEPENDENCIES += yquake2

YQUAKE2_ZAERO_BUILD_ARGS = YQ2_OSTYPE=Linux

ifeq ($(BR2_aarch64),y)
    YQUAKE2_ZAERO_BUILD_ARGS += YQ2_ARCH=aarch64
else ifeq ($(BR2_arm),y)
    YQUAKE2_ZAERO_BUILD_ARGS += YQ2_ARCH=arm
else ifeq ($(BR2_x86_64),y)
    YQUAKE2_ZAERO_BUILD_ARGS += YQ2_ARCH=x86_64
else ifeq ($(BR2_i386),y)
    YQUAKE2_ZAERO_BUILD_ARGS += YQ2_ARCH=i386
endif

define YQUAKE2_ZAERO_BUILD_CMDS
    $(MAKE) $(TARGET_CONFIGURE_OPTS) $(YQUAKE2_ZAERO_BUILD_ARGS) -C $(@D)
endef

define YQUAKE2_ZAERO_INSTALL_TARGET_CMDS
    mkdir -p $(TARGET_DIR)/usr/bin/yquake2/zaero
    $(INSTALL) -D -m 0644 $(@D)/release/game.so \
        $(TARGET_DIR)/usr/bin/yquake2/zaero/
endef

$(eval $(generic-package))
