################################################################################
#
# XBOXDRV
#
################################################################################
XBOXDRV_VERSION = 18c5fabf3bdaa06a541caa6126a06f262e1174b2
XBOXDRV_SITE =  $(call github,Grumbel,xboxdrv,$(XBOXDRV_VERSION))
XBOXDRV_DEPENDENCIES = libusb dbus-python host-scons

define XBOXDRV_BUILD_CMDS
        CFLAGS="$(TARGET_CFLAGS) -I$(STAGING_DIR)/usr/include" CXXFLAGS="$(TARGET_CXXFLAGS) -I$(STAGING_DIR)/usr/include" LD_FLAGS="$(TARGET_LDFLAGS)" \
	$(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D) PREFIX="/usr"
endef

define XBOXDRV_INSTALL_TARGET_CMDS
        CFLAGS="$(TARGET_CFLAGS)" CXXFLAGS="$(TARGET_CXXFLAGS)" $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D) install-exec DESTDIR="$(TARGET_DIR)" PREFIX="/usr"
endef

define XBOXDRV_HOOK_SCONS
	$(SED) "s|dbus-binding-tool|$(HOST_DIR)/usr/bin/dbus-binding-tool|g" $(@D)/SConstruct
	$(SED) "s|pkg-config|$(HOST_DIR)/usr/bin/pkg-config|g" $(@D)/SConstruct
	$(SED) "s|^\(\s*\)scons|\1$(SCONS) CXX=\"$(TARGET_CXX)\" CC=\"$(TARGET_CC)\" CCFLAGS=\"$(TARGET_CFLAGS)\" CXXFLAGS=\"$(TARGET_CXXFLAGS)\"|g" $(@D)/Makefile

endef

XBOXDRV_PRE_CONFIGURE_HOOKS += XBOXDRV_HOOK_SCONS


$(eval $(generic-package))
