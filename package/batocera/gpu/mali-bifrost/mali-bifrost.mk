################################################################################
#
# mali-bifrost
#
################################################################################

MALI_BIFROST_VERSION = 4cbf211cfd9b07854aab4978e50b1151052c6d4c
MALI_BIFROST_SITE = $(call github,LibreELEC,libmali,$(MALI_BIFROST_VERSION))

MALI_BIFROST_INSTALL_STAGING = YES
MALI_BIFROST_PROVIDES = libegl libgles
MALI_BIFROST_DEPENDENCIES = wayland

define MALI_BIFROST_INSTALL_STAGING_CMDS
	mkdir -p $(STAGING_DIR)/usr/lib/pkgconfig
	cp $(@D)/lib/arm-linux-gnueabihf/libmali-bifrost-g52-r16p0-gbm.so $(STAGING_DIR)/usr/lib/libmali.so

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

define MALI_BIFROST_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/usr/lib
	cp $(@D)/lib/arm-linux-gnueabihf/libmali-bifrost-g52-r16p0-gbm.so $(TARGET_DIR)/usr/lib/libmali.so

	(cd $(TARGET_DIR)/usr/lib && ln -sf libmali.so libEGL.so)
	(cd $(TARGET_DIR)/usr/lib && ln -sf libmali.so libEGL.so.1)
	(cd $(TARGET_DIR)/usr/lib && ln -sf libmali.so libgbm.so)
	(cd $(TARGET_DIR)/usr/lib && ln -sf libmali.so libGLESv2.so)
	(cd $(TARGET_DIR)/usr/lib && ln -sf libmali.so libGLESv2.so.2)
endef

$(eval $(generic-package))
