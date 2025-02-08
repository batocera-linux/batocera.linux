################################################################################
#
# mali-G52
#
################################################################################

MALI_G52_VERSION = 1.4-r44p0-202311
MALI_G52_SITE = https://dl.khadas.com/repos/vim4/pool/main/l/linux-gpu-mali-wayland
MALI_G52_SOURCE = linux-gpu-mali-wayland_$(MALI_G52_VERSION)_arm64.deb
MALI_G52_LICENSE = Proprietary
MALI_G52_INSTALL_STAGING = YES

MALI_G52_PROVIDES = libegl libgbm libgles libmali
MALI_G52_DEPENDENCIES = host-patchelf libdrm libglvnd wayland

define MALI_G52_EXTRACT_CMDS
	$(AR) --output=$(@D) -x $(MALI_G52_DL_DIR)/$(MALI_G52_SOURCE)
	$(TAR) xf $(@D)/data.tar.xz -C $(@D)
endef

define MALI_G52_INSTALL_STAGING_CMDS
        mkdir -p $(STAGING_DIR)/usr/lib/pkgconfig
        cp -R $(@D)/etc/* $(STAGING_DIR)/etc/
        cp -R $(@D)/usr/include/* $(STAGING_DIR)/usr/include/
        cp -R $(@D)/usr/lib/aarch64-linux-gnu/* $(STAGING_DIR)/usr/lib/
endef

define MALI_G52_INSTALL_TARGET_CMDS
        mkdir -p $(TARGET_DIR)/usr/lib/pkgconfig
        cp -R $(@D)/etc/* $(TARGET_DIR)/etc/
        cp -R $(@D)/usr/lib/aarch64-linux-gnu/* $(TARGET_DIR)/usr/lib/
        install -D -m 0755 \
            $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/gpu/mali-G52/mali_g52_gpu_launch_hooks.sh \
            $(TARGET_DIR)/usr/share/batocera/configgen/scripts/mali_g52_gpu_launch_hooks.sh
endef

$(eval $(generic-package))
