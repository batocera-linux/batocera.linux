################################################################################
#
# mali-g31-gbm
#
################################################################################
# Version.: Commits on Jan 27, 2021
MALI_G31_GBM_VERSION = 6141ad6e6f2d3eb38e7e0962f61b78510b2e2d2c
MALI_G31_GBM_SITE = $(call github,rockchip-linux,libmali,$(MALI_G31_GBM_VERSION))

MALI_G31_GBM_INSTALL_STAGING = YES
MALI_G31_GBM_PROVIDES = libegl libgles libmali

MALI_G31_GBM_CONF_OPTS = \
	-Dplatform=gbm \
	-Dgpu=bifrost-g31 \
	-Dversion=rxp0

ifneq ($(BR2_PACKAGE_MESA3D),y)
# See https://github.com/rockchip-linux/libmali/issues/66
define MALI_G31_GBM_COPY_KHRPLATFORM_STAGING
	cp $(STAGING_DIR)/usr/include/KHR/mali_khrplatform.h \
		$(STAGING_DIR)/usr/include/KHR/khrplatform.h
endef
MALI_G31_GBM_POST_INSTALL_STAGING_HOOKS += MALI_G31_GBM_COPY_KHRPLATFORM_STAGING
endif

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_ODROIDGOA),y)
# See https://wiki.odroid.com/odroid_go_advance/application_note/vulkan_on_rk3326
define MALI_G31_GBM_RK3326_VULKAN_DRIVER_TARGET_32
	cd $(@D) && \
	wget https://dn.odroid.com/RK3326/ODROID-GO-Advance/rk3326_r13p0_gbm_with_vulkan_and_cl.zip && \
	unzip rk3326_r13p0_gbm_with_vulkan_and_cl.zip && \
	cp $(@D)/libmali.so_rk3326_gbm_arm32_r13p0_with_vulkan_and_cl $(TARGET_DIR)/usr/lib/libmali-bifrost-g31-rxp0-gbm.so && \
	ln -s /usr/lib/libmali-bifrost-g31-rxp0-gbm.so  $(TARGET_DIR)/usr/lib/libvulkan.so && \
	ln -s /usr/lib/libmali-bifrost-g31-rxp0-gbm.so  $(TARGET_DIR)/usr/lib/libvulkan.so.1
endef
define MALI_G31_GBM_RK3326_VULKAN_DRIVER_TARGET_64
	cd $(@D) && \
	wget https://dn.odroid.com/RK3326/ODROID-GO-Advance/rk3326_r13p0_gbm_with_vulkan_and_cl.zip && \
	unzip rk3326_r13p0_gbm_with_vulkan_and_cl.zip && \
	cp $(@D)/libmali.so_rk3326_gbm_arm64_r13p0_with_vulkan_and_cl $(TARGET_DIR)/usr/lib/libmali-bifrost-g31-rxp0-gbm.so && \
	ln -s /usr/lib/libmali-bifrost-g31-rxp0-gbm.so  $(TARGET_DIR)/usr/lib/libvulkan.so && \
	ln -s /usr/lib/libmali-bifrost-g31-rxp0-gbm.so  $(TARGET_DIR)/usr/lib/libvulkan.so.1
endef
ifeq ($(BR2_arm),y)
MALI_G31_GBM_POST_INSTALL_TARGET_HOOKS += MALI_G31_GBM_RK3326_VULKAN_DRIVER_TARGET_32
endif
ifeq ($(BR2_aarch64),y)
MALI_G31_GBM_POST_INSTALL_TARGET_HOOKS += MALI_G31_GBM_RK3326_VULKAN_DRIVER_TARGET_64
endif

endif

$(eval $(meson-package))
