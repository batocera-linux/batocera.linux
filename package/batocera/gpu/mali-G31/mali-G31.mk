################################################################################
#
# mali-G31
#
################################################################################

MALI_G31_VERSION = 2e33bb43d343336fbcf1f4d4a241af6c04f6af3d
MALI_G31_SITE = $(call github,Multi-Retropie,vim1s-g31,$(MALI_G31_VERSION))
MALI_G31_LICENSE = Proprietary
MALI_G31_LICENSE_FILES = END_USER_LICENCE_AGREEMENT.txt
MALI_G31_INSTALL_STAGING = YES

MALI_G31_EXTRA_DOWNLOADS = https://gitlab.freedesktop.org/glvnd/libglvnd/-/archive/master/libglvnd-master.tar.gz

MALI_G31_PROVIDES = libegl libgbm libgles libmali
MALI_G31_DEPENDENCIES = host-patchelf libdrm libglvnd wayland

define MALI_G31_INSTALL_STAGING_CMDS
        mkdir -p $(STAGING_DIR)/usr/lib/pkgconfig
        cp -R $(@D)/etc/* $(STAGING_DIR)/etc/
        cp -R $(@D)/usr/include/* $(STAGING_DIR)/usr/include/
        cp -R $(@D)/usr/lib/aarch64-linux-gnu/* $(STAGING_DIR)/usr/lib/
endef

define MALI_G31_INSTALL_TARGET_CMDS
        mkdir -p $(TARGET_DIR)/usr/lib/pkgconfig
        cp -R $(@D)/etc/* $(TARGET_DIR)/etc/
        cp -R $(@D)/usr/include/* $(TARGET_DIR)/usr/include/
        cp -R $(@D)/usr/lib/aarch64-linux-gnu/* $(TARGET_DIR)/usr/lib/
endef

$(eval $(generic-package))
