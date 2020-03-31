################################################################################
#
# mali-g31-gbm
#
################################################################################
# Version.: Commits on Jan 6, 2020
MALI_G31_GBM_VERSION = f226e982386287a4df669e2832d9ddd613d4153b
MALI_G31_GBM_SITE = $(call github,rockchip-linux,libmali,$(MALI_G31_GBM_VERSION))

MALI_G31_GBM_INSTALL_STAGING = YES
MALI_G31_GBM_PROVIDES = libegl libgles

define MALI_G31_GBM_INSTALL_STAGING_CMDS
	mkdir -p $(STAGING_DIR)/usr/lib/pkgconfig

	cp $(@D)/lib/arm-linux-gnueabihf/libmali-bifrost-g31-rxp0-gbm.so \
		$(STAGING_DIR)/usr/lib/libmali.so

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

	for X in gbm egl glesv2; \
	do \
		cp $(@D)/pkgconfig/$${X}.pc.cmake                	$(STAGING_DIR)/usr/lib/pkgconfig/$${X}.pc; \
		sed -i -e s+@CMAKE_INSTALL_INCLUDEDIR@+include+g 	$(STAGING_DIR)/usr/lib/pkgconfig/$${X}.pc; \
		sed -i -e s+@CMAKE_INSTALL_LIBDIR@+lib+g         	$(STAGING_DIR)/usr/lib/pkgconfig/$${X}.pc; \
	done
endef

define MALI_G31_GBM_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/usr/lib

	cp $(@D)/lib/arm-linux-gnueabihf/libmali-bifrost-g31-rxp0-gbm.so \
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
