################################################################################
#
# mali mp400 gbm
#
################################################################################
# Version.: Commits on Feb 24, 2022
MALI_MP400_GBM_VERSION = b35e1b288bdac91a7d401edd04c71ec9fa573040
MALI_MP400_GBM_SITE = $(call github,caesar-github,libmali,$(MALI_MP400_GBM_VERSION))

MALI_MP400_GBM_INSTALL_STAGING = YES
MALI_MP400_GBM_PROVIDES = libegl libgles libmali
MALI_MP400_GBM_DEPENDENCIES = libdrm

define MALI_MP400_GBM_INSTALL_STAGING_CMDS
	mkdir -p $(STAGING_DIR)/usr/lib/pkgconfig

	cp $(@D)/lib/arm-linux-gnueabihf/libmali-utgard-400-r7p0-r1p1-gbm.so \
		$(STAGING_DIR)/usr/lib/libmali.so

	(cd $(STAGING_DIR)/usr/lib && ln -sf libmali.so libMali.so)
	(cd $(STAGING_DIR)/usr/lib && ln -sf libmali.so libmali.so.1)
	(cd $(STAGING_DIR)/usr/lib && ln -sf libmali.so libEGL.so)
	(cd $(STAGING_DIR)/usr/lib && ln -sf libmali.so libEGL.so.1)
	(cd $(STAGING_DIR)/usr/lib && ln -sf libmali.so libGLESv1_CM.so)
	(cd $(STAGING_DIR)/usr/lib && ln -sf libmali.so libGLESv1_CM.so.1)
	(cd $(STAGING_DIR)/usr/lib && ln -sf libmali.so libGLESv2.so)
	(cd $(STAGING_DIR)/usr/lib && ln -sf libmali.so libGLESv2.so.2)
	(cd $(STAGING_DIR)/usr/lib && ln -sf libmali.so libgbm.so)
	(cd $(STAGING_DIR)/usr/lib && ln -sf libmali.so libgbm.so.1)
	(cd $(STAGING_DIR)/usr/lib && ln -sf libmali.so libOpenCL.so)
	(cd $(STAGING_DIR)/usr/lib && ln -sf libmali.so libOpenCL.so.1)
	(cd $(STAGING_DIR)/usr/lib && ln -sf libmali.so libgbm-egl.so)
	(cd $(STAGING_DIR)/usr/lib && ln -sf libmali.so libgbm-egl.so.1)

	cp -pr $(@D)/include	$(STAGING_DIR)/usr
	cp $(@D)/include/GBM/gbm.h 	$(STAGING_DIR)/usr/include/gbm.h

        for X in gbm egl glesv1_cm glesv2; \
        do \
                cp  $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/gpu/mali-mp400-gbm/pkgconfig/$${X}.pc.cmake                       $(STAGING_DIR)/usr/lib/pkgconfig/$${X}.pc; \
                sed -i -e s+@CMAKE_INSTALL_INCLUDEDIR@+include+g        $(STAGING_DIR)/usr/lib/pkgconfig/$${X}.pc; \
                sed -i -e s+@CMAKE_INSTALL_LIBDIR@+lib+g                $(STAGING_DIR)/usr/lib/pkgconfig/$${X}.pc; \
        done


endef

define MALI_MP400_GBM_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/usr/lib
	
	cp $(@D)/lib/arm-linux-gnueabihf/libmali-utgard-400-r7p0-r1p1-gbm.so \
		$(TARGET_DIR)/usr/lib/libmali.so

	(cd $(TARGET_DIR)/usr/lib && ln -sf libmali.so libMali.so)
	(cd $(TARGET_DIR)/usr/lib && ln -sf libmali.so libmali.so.1)
	(cd $(TARGET_DIR)/usr/lib && ln -sf libmali.so libEGL.so)
	(cd $(TARGET_DIR)/usr/lib && ln -sf libmali.so libEGL.so.1)
	(cd $(TARGET_DIR)/usr/lib && ln -sf libmali.so libGLESv1_CM.so)
	(cd $(TARGET_DIR)/usr/lib && ln -sf libmali.so libGLESv1_CM.so.1)
	(cd $(TARGET_DIR)/usr/lib && ln -sf libmali.so libGLESv2.so)
	(cd $(TARGET_DIR)/usr/lib && ln -sf libmali.so libGLESv2.so.2)
	(cd $(TARGET_DIR)/usr/lib && ln -sf libmali.so libgbm.so)
	(cd $(TARGET_DIR)/usr/lib && ln -sf libmali.so libgbm.so.1)
	(cd $(TARGET_DIR)/usr/lib && ln -sf libmali.so libOpenCL.so)
	(cd $(TARGET_DIR)/usr/lib && ln -sf libmali.so libOpenCL.so.1)
	(cd $(TARGET_DIR)/usr/lib && ln -sf libmali.so libgbm-egl.so)
	(cd $(TARGET_DIR)/usr/lib && ln -sf libmali.so libgbm-egl.so.1)
endef

$(eval $(generic-package))
