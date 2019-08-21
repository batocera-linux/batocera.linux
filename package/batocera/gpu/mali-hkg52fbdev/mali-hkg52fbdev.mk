################################################################################
#
# mali-hkg52fbdev
#
################################################################################

MALI_HKG52FBDEV_VERSION = 7bddce621a0c1e0cc12cfc8b707e93eb37fc0f82
MALI_HKG52FBDEV_SITE = $(call github,hardkernel,buildroot_linux_amlogic_meson_mali,$(MALI_HKG52FBDEV_VERSION))

MALI_HKG52FBDEV_INSTALL_STAGING = YES
MALI_HKG52FBDEV_PROVIDES = libegl libgles

ifeq ($(BR2_arm),y)
  MALI_HKG52FBDEV_LIBDIR=eabihf
else
  MALI_HKG52FBDEV_LIBDIR=arm64
endif

define MALI_HKG52FBDEV_INSTALL_STAGING_CMDS
	mkdir -p $(STAGING_DIR)/usr/lib/pkgconfig
        cp -r $(@D)/lib/$(MALI_HKG52FBDEV_LIBDIR)/gondul/r12p0/fbdev/libMali.so $(STAGING_DIR)/usr/lib

	(cd $(STAGING_DIR)/usr/lib && ln -sf libMali.so libEGL.so)
	(cd $(STAGING_DIR)/usr/lib && ln -sf libMali.so libEGL.so.1)
	(cd $(STAGING_DIR)/usr/lib && ln -sf libMali.so libgbm.so)
	(cd $(STAGING_DIR)/usr/lib && ln -sf libMali.so libGLESv2.so)
	(cd $(STAGING_DIR)/usr/lib && ln -sf libMali.so libGLESv2.so.2)

	cp -pr $(@D)/include              $(STAGING_DIR)/usr
	cp $(@D)/include/EGL_platform/platform_fbdev/*.h $(STAGING_DIR)/usr/include/EGL/
	cp $(@D)/lib/pkgconfig/egl.pc     $(STAGING_DIR)/usr/lib/pkgconfig/egl.pc
	cp $(@D)/lib/pkgconfig/glesv2.pc     $(STAGING_DIR)/usr/lib/pkgconfig/glesv2.pc
endef

define MALI_HKG52FBDEV_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/usr/lib
	cp -r $(@D)/lib/$(MALI_HKG52FBDEV_LIBDIR)/gondul/r12p0/fbdev/libMali.so $(TARGET_DIR)/usr/lib

	(cd $(TARGET_DIR)/usr/lib && ln -sf libMali.so libEGL.so)
	(cd $(TARGET_DIR)/usr/lib && ln -sf libMali.so libEGL.so.1)
	(cd $(TARGET_DIR)/usr/lib && ln -sf libMali.so libgbm.so)
	(cd $(TARGET_DIR)/usr/lib && ln -sf libMali.so libGLESv2.so)
	(cd $(TARGET_DIR)/usr/lib && ln -sf libMali.so libGLESv2.so.2)
endef

$(eval $(generic-package))
