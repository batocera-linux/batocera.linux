################################################################################
#
# mali-g31-gbm
#
################################################################################
# Version: Jun 11, 2021
MALI_G31_GBM_VERSION = ad4c28932c3d07c75fc41dd4a3333f9013a25e7f

MALI_G31_GBM_SOURCE = libmali-$(MALI_G31_GBM_VERSION).tar.gz
MALI_G31_GBM_SITE = https://github.com/batocera-linux/rockchip-packages/releases/download/20220303
#MALI_G31_GBM_SITE = $(call github,rockchip-linux,libmali,$(MALI_G31_GBM_VERSION))

MALI_G31_GBM_DEPENDENCIES = libdrm

MALI_G31_GBM_INSTALL_STAGING = YES
MALI_G31_GBM_PROVIDES = libegl libgles libmali

MALI_G31_GBM_CONF_OPTS = \
	-Dplatform=gbm \
	-Dgpu=bifrost-g31 \
	-Dversion=rxp0

ifneq ($(BR2_PACKAGE_MESA3D),y)
MALI_G31_GBM_CONF_OPTS += -Dkhr-header=true
endif

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RK3326),y)
# See https://wiki.odroid.com/odroid_go_advance/application_note/vulkan_on_rk3326
MALI_G31_GBM_EXTRA_DOWNLOADS=https://dn.odroid.com/RK3326/ODROID-GO-Advance/rk3326_r13p0_gbm_with_vulkan_and_cl.zip

ifeq ($(BR2_aarch64),y)
MALI_G31_GBM_RK3326_BLOB = libmali.so_rk3326_gbm_arm64_r13p0_with_vulkan_and_cl
else
MALI_G31_GBM_RK3326_BLOB = libmali.so_rk3326_gbm_arm32_r13p0_with_vulkan_and_cl
endif

MALI_G31_GBM_TARGET_SO = $(TARGET_DIR)/usr/lib/libmali-bifrost-g31-r13p0-gbm-with-vulkan-and-opencl.so

define MALI_G31_GBM_RK3326_INSTALL
	# Replace driver with HardKernel one
	$(UNZIP) -ob $(MALI_G31_GBM_DL_DIR)/rk3326_r13p0_gbm_with_vulkan_and_cl.zip $(MALI_G31_GBM_RK3326_BLOB) -d $(@D)
	$(INSTALL) -D -m 0755 $(@D)/$(MALI_G31_GBM_RK3326_BLOB) $(MALI_G31_GBM_TARGET_SO)
	rm -f $(TARGET_DIR)/usr/lib/libmali-bifrost-g31-rxp0-gbm.so $(TARGET_DIR)/usr/lib/libmali.so.1.9.0
	ln -sfr $(MALI_G31_GBM_TARGET_SO) $(TARGET_DIR)/usr/lib/libmali.so.1.9.0

	# Install Vulkan driver as ICD through vulkan-loader
	mkdir -p $(TARGET_DIR)/usr/share/vulkan/icd.d
	$(INSTALL) -D -m 0755 $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/gpu/mali-g31-gbm/mali_icd.json $(TARGET_DIR)/usr/share/vulkan/icd.d/

	# Ugly workaround to fix duckstation compilation
	rm $(STAGING_DIR)/usr/lib/libEGL.so
	ln -sfr $(STAGING_DIR)/usr/lib/libmali.so $(STAGING_DIR)/usr/lib/libEGL.so
endef

MALI_G31_GBM_POST_INSTALL_TARGET_HOOKS += MALI_G31_GBM_RK3326_INSTALL
endif

$(eval $(meson-package))
