################################################################################
#
# sonic2013
#
################################################################################

SONIC2013_VERSION = 1.3.2
SONIC2013_SITE = https://github.com/RSDKModding/RSDKv4-Decompilation
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

$(eval $(generic-package))
