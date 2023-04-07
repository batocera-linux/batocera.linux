################################################################################
#
# mali-G52
#
################################################################################

MALI_G52_VERSION = 309268f7a34ca0bba0ab94a0b09feb0191c77fb8
MALI_G52_SITE = $(call github,JeffyCN,mirrors,$(MALI_G52_VERSION))
MALI_G52_LICENSE = Proprietary
MALI_G52_LICENSE_FILES = END_USER_LICENCE_AGREEMENT.txt
MALI_G52_INSTALL_STAGING = YES

MALI_G52_EXTRA_DOWNLOADS = https://gitlab.freedesktop.org/glvnd/libglvnd/-/archive/master/libglvnd-master.tar.gz

MALI_G52_PROVIDES = libegl libgbm libgles libmali
MALI_G52_DEPENDENCIES = host-patchelf libdrm libglvnd

MALI_G52_GPU = bifrost-G52
MALI_G52_VER = g2p0
MALI_G52_PLATFORM = wayland-gbm
MALI_G52_MESA_HEADER_DIRS = KHR EGL GLES GLES2 GLES3
MALI_G52_ROCKCHIP_HEADER_DIRS = GBM
MALI_G52_CONF_OPTS += \
   -Dwith-overlay=false \
   -Dopencl-icd=false \
   -Dkhr-header=true \
   -Dgpu=$(MALI_G52_GPU) \
   -Dversion=$(MALI_G52_VER) \
   -Dplatform=$(subst $(eval) $(eval),-,$(MALI_G52_PLATFORM)) \
   -Dwrappers=auto \
   -Dhooks=true

$(eval $(meson-package))
