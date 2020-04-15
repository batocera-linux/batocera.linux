################################################################################
#
# mali-T760
#
################################################################################

MALI_T760_VERSION = 4cbf211cfd9b07854aab4978e50b1151052c6d4c
MALI_T760_SITE = $(call github,LibreELEC,libmali,$(MALI_T760_VERSION))

MALI_T760_INSTALL_STAGING = YES
MALI_T760_PROVIDES = libegl libgles

MALI_T760_TARGET_DIR=$(TARGET_DIR)
MALI_T760_STAGING_DIR=$(STAGING_DIR)
MALI_T760_LIBDIR=arm-linux-gnueabihf

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_MIQI),y)
MALI_T760_LIBFILE=libmali-midgard-t76x-r14p0-r1p0-gbm.so
else
MALI_T760_LIBFILE=libmali-midgard-t76x-r14p0-r0p0-gbm.so
endif

define MALI_T760_INSTALL_STAGING_CMDS
	mkdir -p $(MALI_T760_STAGING_DIR)
    cp -r $(@D)/lib/$(MALI_T760_LIBDIR)/$(MALI_T760_LIBFILE) $(MALI_T760_STAGING_DIR)/usr/lib
    (cd $(MALI_T760_STAGING_DIR)/usr/lib && ln -sf $(MALI_T760_LIBFILE) libmali.so)
	(cd $(MALI_T760_STAGING_DIR)/usr/lib && ln -sf libmali.so libEGL.so)
	(cd $(MALI_T760_STAGING_DIR)/usr/lib && ln -sf libmali.so libEGL.so.1)
	(cd $(MALI_T760_STAGING_DIR)/usr/lib && ln -sf libmali.so libgbm.so)
	(cd $(MALI_T760_STAGING_DIR)/usr/lib && ln -sf libmali.so libGLESv2.so)
	(cd $(MALI_T760_STAGING_DIR)/usr/lib && ln -sf libmali.so libGLESv2.so.2)
	(cd $(MALI_T760_STAGING_DIR)/usr/lib && ln -sf libmali.so libMali.so)

	cp -pr $(@D)/include $(MALI_T760_STAGING_DIR)/usr
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/gpu/mali-T760/gbm.pc $(MALI_T760_STAGING_DIR)/usr/lib/pkgconfig/gbm.pc
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/gpu/mali-T760/egl.pc $(MALI_T760_STAGING_DIR)/usr/lib/pkgconfig/egl.pc
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/gpu/mali-T760/glesv2.pc $(MALI_T760_STAGING_DIR)/usr/lib/pkgconfig/glesv2.pc
endef

define MALI_T760_INSTALL_TARGET_CMDS
    mkdir -p $(MALI_T760_TARGET_DIR)
    cp -r $(@D)/lib/$(MALI_T760_LIBDIR)/$(MALI_T760_LIBFILE) $(MALI_T760_TARGET_DIR)/usr/lib
    (cd $(MALI_T760_TARGET_DIR)/usr/lib && ln -sf $(MALI_T760_LIBFILE) libmali.so)
	(cd $(MALI_T760_TARGET_DIR)/usr/lib && ln -sf libmali.so libEGL.so)
	(cd $(MALI_T760_TARGET_DIR)/usr/lib && ln -sf libmali.so libEGL.so.1)
	(cd $(MALI_T760_TARGET_DIR)/usr/lib && ln -sf libmali.so libgbm.so)
	(cd $(MALI_T760_TARGET_DIR)/usr/lib && ln -sf libmali.so libGLESv2.so)
	(cd $(MALI_T760_TARGET_DIR)/usr/lib && ln -sf libmali.so libGLESv2.so.2)
	(cd $(MALI_T760_TARGET_DIR)/usr/lib && ln -sf libmali.so libMali.so)
endef

$(eval $(generic-package))
