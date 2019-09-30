################################################################################
#
# libmali
#
################################################################################

LIBMALI_VERSION = 4cbf211cfd9b07854aab4978e50b1151052c6d4c
LIBMALI_SITE = $(call github,LibreELEC,libmali,$(LIBMALI_VERSION))

LIBMALI_INSTALL_STAGING = YES
LIBMALI_PROVIDES = libegl libgles

ifeq ($(BR2_PACKAGE_LIBMALI_T620_WAYLAND)$(BR2_PACKAGE_LIBMALI_BIFROST_WAYLAND),y)
	LIBMALI_DEPENDENCIES = wayland
endif

ifeq ($(BR2_PACKAGE_LIBMALI_BIFROST_WAYLAND),y)
	BR2_PACKAGE_LIBMALI_SRCLIB=libmali-bifrost-g52-r16p0-gbm.so
endif

ifeq ($(BR2_PACKAGE_LIBMALI_T620_WAYLAND),y)
	BR2_PACKAGE_LIBMALI_SRCLIB=libmali-midgard-t620-r12p0-wayland-gbm.so
endif

define LIBMALI_INSTALL_STAGING_CMDS
	mkdir -p $(STAGING_DIR)/usr/lib/pkgconfig

	cp $(@D)/lib/arm-linux-gnueabihf/$(BR2_PACKAGE_LIBMALI_SRCLIB) $(STAGING_DIR)/usr/lib/libmali.so

	(cd $(STAGING_DIR)/usr/lib && ln -sf libmali.so libEGL.so)
	(cd $(STAGING_DIR)/usr/lib && ln -sf libmali.so libEGL.so.1)
	(cd $(STAGING_DIR)/usr/lib && ln -sf libmali.so libgbm.so)
	(cd $(STAGING_DIR)/usr/lib && ln -sf libmali.so libGLESv2.so)
	(cd $(STAGING_DIR)/usr/lib && ln -sf libmali.so libGLESv2.so.2)

	cp -pr $(@D)/include              $(STAGING_DIR)/usr
	cp $(@D)/include/gbm.h $(STAGING_DIR)/usr/include/gbm.h

	for X in gbm egl glesv1_cm glesv2; \
	do \
		cp $(@D)/pkgconfig/$${X}.pc.cmake                 $(STAGING_DIR)/usr/lib/pkgconfig/$${X}.pc; \
		sed -i -e s+@CMAKE_INSTALL_INCLUDEDIR@+include+g $(STAGING_DIR)/usr/lib/pkgconfig/$${X}.pc; \
		sed -i -e s+@CMAKE_INSTALL_LIBDIR@+lib+g         $(STAGING_DIR)/usr/lib/pkgconfig/$${X}.pc; \
	done
endef

define LIBMALI_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/usr/lib
	cp $(@D)/lib/arm-linux-gnueabihf/$(BR2_PACKAGE_LIBMALI_SRCLIB) $(TARGET_DIR)/usr/lib/libmali.so

	(cd $(TARGET_DIR)/usr/lib && ln -sf libmali.so libEGL.so)
	(cd $(TARGET_DIR)/usr/lib && ln -sf libmali.so libEGL.so.1)
	(cd $(TARGET_DIR)/usr/lib && ln -sf libmali.so libgbm.so)
	(cd $(TARGET_DIR)/usr/lib && ln -sf libmali.so libGLESv2.so)
	(cd $(TARGET_DIR)/usr/lib && ln -sf libmali.so libGLESv2.so.2)
endef

$(eval $(generic-package))
