################################################################################
#
# XBOXDRV
#
################################################################################
XBOXDRV_VERSION = fb787abe320741d8c341a9ad62c9a0ec513fc2cb
XBOXDRV_SITE =  $(call github,Grumbel,xboxdrv,$(XBOXDRV_VERSION))
XBOXDRV_DEPENDENCIES = libusb dbus-python
#opts.Add('CPPPATH', 'Additional preprocessor paths')
#opts.Add('CPPFLAGS', 'Additional preprocessor flags')
#opts.Add('CPPDEFINES', 'defined constants')
#opts.Add('LIBPATH', 'Additional library paths')
#opts.Add('LIBS', 'Additional libraries')
#opts.Add('LINKFLAGS', 'Linker Compiler flags')
#opts.Add('BUILD', 'Build type: release, custom, development')

define XBOXDRV_BUILD_CMDS
        CFLAGS="$(TARGET_CFLAGS) -I$(STAGING_DIR)/usr/include" CXXFLAGS="$(TARGET_CXXFLAGS) -I$(STAGING_DIR)/usr/include" LD_FLAGS="$(TARGET_LDFLAGS)" $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D)
endef

define XBOXDRV_INSTALL_TARGET_CMDS
        CFLAGS="$(TARGET_CFLAGS)" CXXFLAGS="$(TARGET_CXXFLAGS)" $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D) install-exec DESTDIR="$(TARGET_DIR)"
endef

define XBOXDRV_HOOK_SCONS
	$(SED) "s|dbus-binding-tool|$(HOST_DIR)/usr/bin/dbus-binding-tool|g" $(@D)/SConstruct
	$(SED) "s|pkg-config|$(HOST_DIR)/usr/bin/pkg-config|g" $(@D)/SConstruct
	$(SED) "s|scons|$(HOST_DIR)/usr/bin/scons CXX=\"$(TARGET_CXX)\" CC=\"$(TARGET_CC)\" CCFLAGS=\"$(TARGET_CFLAGS)\" CXXFLAGS=\"$(TARGET_CXXFLAGS)\"|g" $(@D)/Makefile
endef

XBOXDRV_PRE_CONFIGURE_HOOKS += XBOXDRV_HOOK_SCONS


$(eval $(generic-package))
