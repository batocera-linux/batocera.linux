################################################################################
#
# mali g52
#
################################################################################
# Version.: Commits on Nov 13, 2019
MALI_G52_VERSION = 4cbf211cfd9b07854aab4978e50b1151052c6d4c
MALI_G52_SITE = $(call github,LibreELEC,libmali,$(MALI_G52_VERSION))

MALI_G52_INSTALL_STAGING = YES
MALI_G52_PROVIDES = libegl libgles
MALI_G52_DEPENDENCIES = wayland mali-bifrost-module

MALI_BLOB_FILENAME = libmali-bifrost-g52-r16p0-gbm.so

ifeq ($(BR2_arm),y)
MALI_BLOB = $(@D)/lib/arm-linux-gnueabihf/$(MALI_BLOB_FILENAME)
else
MALI_BLOB = $(@D)/lib/aarch64-linux-gnu/$(MALI_BLOB_FILENAME)
endif

define MALI_G52_INSTALL_STAGING_CMDS
	mkdir -p $(STAGING_DIR)/usr/lib/pkgconfig

	cp $(MALI_BLOB) $(STAGING_DIR)/usr/lib/libmali.so

	(cd $(STAGING_DIR)/usr/lib && ln -sf libmali.so libMali.so)
	(cd $(STAGING_DIR)/usr/lib && ln -sf libmali.so libEGL.so)
	(cd $(STAGING_DIR)/usr/lib && ln -sf libmali.so libEGL.so.1)
	(cd $(STAGING_DIR)/usr/lib && ln -sf libmali.so libGLESv1_CM.so)
	(cd $(STAGING_DIR)/usr/lib && ln -sf libmali.so libGLESv1_CM.so.1)
	(cd $(STAGING_DIR)/usr/lib && ln -sf libmali.so libGLESv2.so)
	(cd $(STAGING_DIR)/usr/lib && ln -sf libmali.so libGLESv2.so.2)
	(cd $(STAGING_DIR)/usr/lib && ln -sf libmali.so libgbm.so)

	cp -pr $(@D)/include    $(STAGING_DIR)/usr
	cp $(@D)/include/gbm.h 	$(STAGING_DIR)/usr/include/gbm.h

	for X in gbm egl glesv1_cm glesv2; \
	do \
		cp $(@D)/pkgconfig/$${X}.pc.cmake                 	$(STAGING_DIR)/usr/lib/pkgconfig/$${X}.pc; \
		sed -i -e s+@CMAKE_INSTALL_INCLUDEDIR@+include+g 	$(STAGING_DIR)/usr/lib/pkgconfig/$${X}.pc; \
		sed -i -e s+@CMAKE_INSTALL_LIBDIR@+lib+g         	$(STAGING_DIR)/usr/lib/pkgconfig/$${X}.pc; \
	done
endef

define MALI_G52_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/usr/lib

	cp $(@D)/lib/arm-linux-gnueabihf/libmali-bifrost-g52-r16p0-gbm.so \
		$(TARGET_DIR)/usr/lib/libmali.so

	(cd $(TARGET_DIR)/usr/lib && ln -sf libmali.so libMali.so)
	(cd $(TARGET_DIR)/usr/lib && ln -sf libmali.so libEGL.so)
	(cd $(TARGET_DIR)/usr/lib && ln -sf libmali.so libEGL.so.1)
	(cd $(TARGET_DIR)/usr/lib && ln -sf libmali.so libGLESv1_CM.so)
	(cd $(TARGET_DIR)/usr/lib && ln -sf libmali.so libGLESv1_CM.so.1)
	(cd $(TARGET_DIR)/usr/lib && ln -sf libmali.so libGLESv2.so)
	(cd $(TARGET_DIR)/usr/lib && ln -sf libmali.so libGLESv2.so.2)
	(cd $(TARGET_DIR)/usr/lib && ln -sf libmali.so libgbm.so)
endef

$(eval $(generic-package))
