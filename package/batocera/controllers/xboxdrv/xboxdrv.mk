################################################################################
#
# XBOXDRV
#
################################################################################
XBOXDRV_VERSION = fbbb7d8b3718b76945b22c195b90ea66401dcb24
XBOXDRV_SITE =  $(call github,xboxdrv,xboxdrv,$(XBOXDRV_VERSION))
XBOXDRV_DEPENDENCIES = libusb dbus-python dbus-glib host-scons boost

define XBOXDRV_BUILD_CMDS
        PATH="$(HOST_DIR)/bin:$$PATH" CFLAGS="$(TARGET_CFLAGS) -I$(STAGING_DIR)/usr/include" CXXFLAGS="$(TARGET_CXXFLAGS) -I$(STAGING_DIR)/usr/include" LD_FLAGS="$(TARGET_LDFLAGS)" \
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
