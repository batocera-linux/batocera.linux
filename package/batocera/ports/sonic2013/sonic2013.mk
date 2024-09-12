################################################################################
#
# sonic2013
#
################################################################################
# Version: Commits on Mar 20, 2024
SONIC2013_VERSION = b78db1b795d6907b0f834765b6bf338abe5a2834
SONIC2013_SITE = https://github.com/Rubberduckycooly/Sonic-1-2-2013-Decompilation.git
SONIC2013_SITE_METHOD = git
SONIC2013_GIT_SUBMODULES == YES
SONIC2013_LICENSE = Custom

SONIC2013_DEPENDENCIES = sdl2 libogg libvorbis

# legacy version for systems that don't support libglew
ifneq ($(BR2_PACKAGE_LIBGLEW),y)
    SONIC2013_VERSION = f9718af
else
    SONIC2013_DEPENDENCIES += libglew
endif

ifeq ($(BR2_PACKAGE_LIBGLU),y)
SONIC2013_DEPENDENCIES += libglu
endif

define SONIC2013_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) -C $(@D) -f Makefile VERBOSE=1
endef

define SONIC2013_INSTALL_TARGET_CMDS
	$(INSTALL) -D -m 0755 $(@D)/bin/RSDKv4 $(TARGET_DIR)/usr/bin/sonic2013
endef

define SONIC2013_POST_PROCESS
	mkdir -p $(TARGET_DIR)/usr/share/evmapy $(TARGET_DIR)/usr/share/sonic2013
	cp -f $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/ports/sonic2013/sonicretro.sonic2013.keys \
	    $(TARGET_DIR)/usr/share/evmapy
endef

SONIC2013_POST_INSTALL_TARGET_HOOKS += SONIC2013_POST_PROCESS

$(eval $(generic-package))
