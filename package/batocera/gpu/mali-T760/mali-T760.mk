################################################################################
#
# mali-T760
#
################################################################################

MALI_T760_VERSION = 43b24f4a2c7cda2144210e6ca6c62eaaf8a29497
MALI_T760_SITE = $(call github,rockchip-linux,libmali,$(MALI_T760_VERSION))
MALI_T760_INSTALL_STAGING = YES
MALI_T760_PROVIDES = libegl libgles
MALI_T760_TARGET_DIR=$(TARGET_DIR)
MALI_T760_STAGING_DIR=$(STAGING_DIR)
ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_MIQI),y)
MALI_T760_LIBFILE=libmali-midgard-t76x-r18p0-r1p0-gbm.so
else
MALI_T760_LIBFILE=libmali-midgard-t76x-r18p0-r0p0-gbm.so
endif

MALI_T760_CONF_OPTS += -Darch=auto -Dgpu=midgard-t76x -Dplatform=gbm -Dsubversion=all

define MALI_T760_INSTALL_STAGING_CMDS
	mkdir -p $(MALI_T760_STAGING_DIR)
	(cd $(MALI_T760_STAGING_DIR)/usr/lib && ln -sf $(MALI_T760_LIBFILE) libmali.so)
	(cd $(MALI_T760_STAGING_DIR)/usr/lib && ln -sf libmali.so libEGL.so)
	(cd $(MALI_T760_STAGING_DIR)/usr/lib && ln -sf libmali.so libEGL.so.1)
	(cd $(MALI_T760_STAGING_DIR)/usr/lib && ln -sf libmali.so libgbm.so)
	(cd $(MALI_T760_STAGING_DIR)/usr/lib && ln -sf libmali.so libGLESv2.so)
        (cd $(MALI_T760_STAGING_DIR)/usr/lib && ln -sf libmali.so libGLESv2.so.1)
	(cd $(MALI_T760_STAGING_DIR)/usr/lib && ln -sf libmali.so libGLESv2.so.2)
	(cd $(MALI_T760_STAGING_DIR)/usr/lib && ln -sf libmali.so libMali.so)
	(cd $(MALI_T760_STAGING_DIR)/usr/lib && ln -sf libmali.so libGLESv1.so)
	(cd $(MALI_T760_STAGING_DIR)/usr/lib && ln -sf libmali.so libGLESv1_CM.so)
	(cd $(MALI_T760_STAGING_DIR)/usr/lib && ln -sf libmali.so libGLESv1_CM.so.1)
	(cd $(MALI_T760_STAGING_DIR)/usr/lib && ln -sf libmali.so libbrcmGLESv2.so)
endef

define MALI_T760_INSTALL_TARGET_CMDS
	mkdir -p $(MALI_T760_TARGET_DIR)
	(cd $(MALI_T760_TARGET_DIR)/usr/lib && ln -sf $(MALI_T760_LIBFILE) libmali.so)
	(cd $(MALI_T760_TARGET_DIR)/usr/lib && ln -sf libmali.so libEGL.so)
	(cd $(MALI_T760_TARGET_DIR)/usr/lib && ln -sf libmali.so libEGL.so.1)
	(cd $(MALI_T760_TARGET_DIR)/usr/lib && ln -sf libmali.so libGLESv1.so)
	(cd $(MALI_T760_TARGET_DIR)/usr/lib && ln -sf libmali.so libGLESv1_CM.so)
	(cd $(MALI_T760_TARGET_DIR)/usr/lib && ln -sf libmali.so libGLESv1_CM.so.1)
	(cd $(MALI_T760_TARGET_DIR)/usr/lib && ln -sf libmali.so libbrcmGLESv2.so)
	(cd $(MALI_T760_TARGET_DIR)/usr/lib && ln -sf libmali.so libgbm.so)
	(cd $(MALI_T760_TARGET_DIR)/usr/lib && ln -sf libmali.so libGLESv2.so)
        (cd $(MALI_T760_TARGET_DIR)/usr/lib && ln -sf libmali.so libGLESv2.so.1)
	(cd $(MALI_T760_TARGET_DIR)/usr/lib && ln -sf libmali.so libGLESv2.so.2)
	(cd $(MALI_T760_TARGET_DIR)/usr/lib && ln -sf libmali.so libMali.so)
endef

$(eval $(meson-package))
