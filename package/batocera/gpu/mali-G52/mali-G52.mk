################################################################################
#
# mali-G52
#
################################################################################

MALI_G52_VERSION = 6ab9d7ce7a991f997460697013fc54029fcac681
MALI_G52_SITE = $(call github,rtissera,a311d2-mali-g52,$(MALI_G52_VERSION))
MALI_G52_LICENSE = Proprietary
MALI_G52_LICENSE_FILES = END_USER_LICENCE_AGREEMENT.txt
MALI_G52_INSTALL_STAGING = YES

MALI_G52_EXTRA_DOWNLOADS = https://gitlab.freedesktop.org/glvnd/libglvnd/-/archive/master/libglvnd-master.tar.gz

MALI_G52_PROVIDES = libegl libgbm libgles libmali
MALI_G52_DEPENDENCIES = host-patchelf libdrm libglvnd wayland

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

#MALI_G52_GPU = bifrost-g52
#MALI_G52_VER = g2p0
#MALI_G52_PLATFORM = wayland-gbm
#MALI_G52_MESA_HEADER_DIRS = KHR EGL GLES GLES2 GLES3
#MALI_G52_ROCKCHIP_HEADER_DIRS = GBM
#MALI_G52_CONF_OPTS += \
#   -Dwith-overlay=false \
#   -Dopencl-icd=false \
#   -Dkhr-header=true \
#   -Dgpu=$(MALI_G52_GPU) \
#   -Dversion=$(MALI_G52_VER) \
#   -Dplatform=$(subst $(eval) $(eval),-,$(MALI_G52_PLATFORM)) \
#   -Dwrappers=auto \
#   -Dhooks=true

$(eval $(generic-package))
