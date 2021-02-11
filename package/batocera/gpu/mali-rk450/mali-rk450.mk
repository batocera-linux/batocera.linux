################################################################################
#
# mali-rk450
#
################################################################################

MALI_RK450_VERSION = 3d777c26fc4ee005c0b92b388b8874e1e77b134b
MALI_RK450_SITE = $(call github,ayufan-rock64,libmali,$(MALI_RK450_VERSION))

MALI_RK450_INSTALL_STAGING = YES
MALI_RK450_PROVIDES = libegl libgles libmali

MALI_RK450_TARGET_DIR=$(TARGET_DIR)
MALI_RK450_STAGING_DIR=$(STAGING_DIR)

ifeq ($(BR2_arm),y)
  MALI_RK450_LIBDIR=arm-linux-gnueabihf
else
  MALI_RK450_LIBDIR=aarch64-linux-gnu
endif

define MALI_RK450_INSTALL_STAGING_CMDS
	mkdir -p $(MALI_RK450_STAGING_DIR)
		cp -r $(@D)/lib/$(MALI_RK450_LIBDIR)/libmali-midgard-t86x-r14p0-gbm.so $(MALI_RK450_STAGING_DIR)/usr/lib

	(cd $(MALI_RK450_STAGING_DIR)/usr/lib && ln -sf libmali-midgard-t86x-r14p0-gbm.so libmali.so)

	(cd $(MALI_RK450_STAGING_DIR)/usr/lib && ln -sf libmali.so libMali.so)
	(cd $(MALI_RK450_STAGING_DIR)/usr/lib && ln -sf libmali.so libEGL.so)
	(cd $(MALI_RK450_STAGING_DIR)/usr/lib && ln -sf libmali.so libEGL.so.1)
	(cd $(MALI_RK450_STAGING_DIR)/usr/lib && ln -sf libmali.so libGLESv1_CM.so)
	(cd $(MALI_RK450_STAGING_DIR)/usr/lib && ln -sf libmali.so libGLESv1_CM.so.1)
	(cd $(MALI_RK450_STAGING_DIR)/usr/lib && ln -sf libmali.so libGLESv2.so)
	(cd $(MALI_RK450_STAGING_DIR)/usr/lib && ln -sf libmali.so libGLESv2.so.2)
	(cd $(MALI_RK450_STAGING_DIR)/usr/lib && ln -sf libmali.so libgbm.so)

	cp -pr $(@D)/include $(MALI_RK450_STAGING_DIR)/usr
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/gpu/mali-rk450/gbm.pc $(MALI_RK450_STAGING_DIR)/usr/lib/pkgconfig/gbm.pc
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/gpu/mali-rk450/egl.pc $(MALI_RK450_STAGING_DIR)/usr/lib/pkgconfig/egl.pc
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/gpu/mali-rk450/glesv2.pc $(MALI_RK450_STAGING_DIR)/usr/lib/pkgconfig/glesv2.pc
endef

define MALI_RK450_INSTALL_TARGET_CMDS
	mkdir -p $(MALI_RK450_TARGET_DIR)
	cp -r $(@D)/lib/$(MALI_RK450_LIBDIR)/libmali-midgard-t86x-r14p0-gbm.so $(MALI_RK450_TARGET_DIR)/usr/lib

	(cd $(MALI_RK450_TARGET_DIR)/usr/lib && ln -sf libmali-midgard-t86x-r14p0-gbm.so libmali.so)

	(cd $(MALI_RK450_TARGET_DIR)/usr/lib && ln -sf libmali.so libMali.so)
	(cd $(MALI_RK450_TARGET_DIR)/usr/lib && ln -sf libmali.so libEGL.so)
	(cd $(MALI_RK450_TARGET_DIR)/usr/lib && ln -sf libmali.so libEGL.so.1)
	(cd $(MALI_RK450_TARGET_DIR)/usr/lib && ln -sf libmali.so libGLESv1_CM.so)
	(cd $(MALI_RK450_TARGET_DIR)/usr/lib && ln -sf libmali.so libGLESv1_CM.so.1)
	(cd $(MALI_RK450_TARGET_DIR)/usr/lib && ln -sf libmali.so libGLESv2.so)
	(cd $(MALI_RK450_TARGET_DIR)/usr/lib && ln -sf libmali.so libGLESv2.so.2)
	(cd $(MALI_RK450_TARGET_DIR)/usr/lib && ln -sf libmali.so libgbm.so)
endef

$(eval $(generic-package))
