################################################################################
#
# mali-G610
#
################################################################################

MALI_G610_VERSION = 309268f7a34ca0bba0ab94a0b09feb0191c77fb8
MALI_G610_SITE = $(call github,JeffyCN,mirrors,$(MALI_G610_VERSION))
MALI_G610_LICENSE = Proprietary
MALI_G610_LICENSE_FILES = END_USER_LICENCE_AGREEMENT.txt
MALI_G610_INSTALL_STAGING = YES

MALI_G610_EXTRA_DOWNLOADS = https://gitlab.freedesktop.org/glvnd/libglvnd/-/archive/master/libglvnd-master.tar.gz

MALI_G610_PROVIDES = libegl libgbm libgles libmali
MALI_G610_DEPENDENCIES = host-patchelf libdrm libglvnd
#MALI_G610_DEPENDENCIES += wayland libxcb xlib_libX11

MALI_G610_GPU = valhall-g610
MALI_G610_VER = g6p0
MALI_G610_PLATFORM = gbm
MALI_G610_MESA_HEADER_DIRS = KHR EGL GLES GLES2 GLES3
MALI_G610_ROCKCHIP_HEADER_DIRS = GBM
MALI_G610_CONF_OPTS += \
   -Dwith-overlay=false \
   -Dopencl-icd=false \
   -Dkhr-header=true \
   -Dgpu=$(MALI_G610_GPU) \
   -Dversion=$(MALI_G610_VER) \
   -Dplatform=$(subst $(eval) $(eval),-,$(MALI_G610_PLATFORM)) \
   -Dwrappers=auto \
   -Dhooks=true

#define MALI_G610_INSTALL_HEADERS
#   tar xvfz $(MALI_G610_DL_DIR)/libglvnd-master.tar.gz -C $(@D)
#   for header_dir in $(MALI_G610_MESA_HEADER_DIRS); do \
#      cp -rpv $(@D)/libglvnd-master/include/$${header_dir} $(STAGING_DIR)/usr/include/ || exit 1; done
#   for header_dir in $(MALI_G610_ROCKCHIP_HEADER_DIRS); do \
#      cp -rpv $(@D)/include/$${header_dir} $(STAGING_DIR)/usr/include/ || exit 1; done
#endef

# define MALI_G610_REMOVE_BROKEN_HOOKS
# 	rm -fv $(STAGING_DIR)/usr/lib/libwayland-egl.so.1
# 	rm -fv $(TARGET_DIR)/usr/lib/libwayland-egl.so.1
# endef

# MALI_G610_PRE_CONFIGURE_HOOKS += MALI_G610_INSTALL_HEADERS
# MALI_G610_POST_INSTALL_TARGET_HOOKS += MALI_G610_REMOVE_BROKEN_HOOKS

$(eval $(meson-package))
