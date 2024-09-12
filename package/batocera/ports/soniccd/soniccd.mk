################################################################################
#
# soniccd
#
################################################################################
# Version: Commits on Mar 22, 2024
SONICCD_SITE = https://github.com/Rubberduckycooly/Sonic-CD-11-Decompilation.git
SONICCD_SITE_METHOD = git
SONICCD_GIT_SUBMODULES = YES
SONICCD_LICENSE = Custom

SONICCD_DEPENDENCIES = sdl2 libogg libvorbis libtheora libglu

ifneq ($(BR2_PACKAGE_LIBGLEW),y)
    SONICCD_VERSION = 222caf6
    SONICCD_BINNAME = soniccd
else
    SONICCD_VERSION = 7a23c39
    SONICCD_BINNAME = RSDKv3
    SONICCD_DEPENDENCIES += libglew
endif

define SONICCD_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) -C $(@D) -f Makefile VERBOSE=1
endef

define SONICCD_INSTALL_TARGET_CMDS
	$(INSTALL) -D -m 0755 $(@D)/bin/$(SONICCD_BINNAME) $(TARGET_DIR)/usr/bin/soniccd
endef

define SONICCD_POST_PROCESS
	mkdir -p $(TARGET_DIR)/usr/share/evmapy $(TARGET_DIR)/usr/share/soniccd
	cp -f $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/ports/soniccd/sonicretro.soniccd.keys \
	    $(TARGET_DIR)/usr/share/evmapy
endef

SONICCD_POST_INSTALL_TARGET_HOOKS += SONICCD_POST_PROCESS

$(eval $(generic-package))
