################################################################################
#
# soniccd
#
################################################################################

SONICCD_SITE = https://github.com/RSDKModding/RSDKv3-Decompilation
SONICCD_SITE_METHOD = git
SONICCD_GIT_SUBMODULES = YES
SONICCD_LICENSE = Custom

SONICCD_DEPENDENCIES = sdl2 libogg libvorbis libtheora

ifneq ($(BR2_PACKAGE_LIBGLEW),y)
    SONICCD_VERSION = 222caf6
    SONICCD_BINNAME = soniccd
else
    SONICCD_VERSION = 1.3.2
    SONICCD_BINNAME = RSDKv3
    SONICCD_DEPENDENCIES += libglew
endif

ifeq ($(BR2_PACKAGE_LIBGLU),y)
    SONICCD_DEPENDENCIES += libglu
endif

define SONICCD_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) -C $(@D) -f Makefile VERBOSE=1
endef

define SONICCD_INSTALL_TARGET_CMDS
	$(INSTALL) -D -m 0755 $(@D)/bin/$(SONICCD_BINNAME) $(TARGET_DIR)/usr/bin/soniccd
endef

$(eval $(generic-package))
