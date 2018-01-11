################################################################################
#
# mali-450
# http://malideveloper.arm.com/resources/drivers/arm-mali-midgard-gpu-user-space-drivers
#
################################################################################

#MALI_450_VERSION = r6p0-01rel0
#MALI_450_VERSION = r5p0-01rel0
#MALI_450_SOURCE = mali-450_r6p0-01rel0_linux_1+arm64.tar.gz
#MALI_450_SOURCE = mali-450_r5p0-01rel0_linux_1+fbdev+arm64-v8a.tar.gz
#MALI_450_SITE = http://malideveloper.arm.com/downloads/drivers/binary/utgard/r6p0-01rel0
#MALI_450_SITE = http://malideveloper.arm.com/downloads/drivers/binary/utgard/r5p0-01rel0
#MALI_450_TARGET_DIR=$(TARGET_DIR)/usr/lib
#MALI_450_STAGING_DIR=$(STAGING_DIR)/usr/lib

#MALI_450_VERSION = r6p1-01rel0
#MALI_450_SOURCE = opengl-meson-gxbb-$(MALI_450_VERSION).tar.xz
#MALI_450_SITE = http://sources.libreelec.tv/devel

MALI_450_VERSION = r6p1-01rel0
MALI_450_SITE = $(call github,batocera-linux,opengl-meson-gxbb,$(MALI_450_VERSION))

MALI_450_INSTALL_STAGING = YES
MALI_450_DEPENDENCIES = mali-opengles-sdk
MALI_450_PROVIDES = libegl libgles

MALI_450_TARGET_DIR=$(TARGET_DIR)
MALI_450_STAGING_DIR=$(STAGING_DIR)

define MALI_450_INSTALL_STAGING_CMDS
	@mkdir -p $(MALI_450_STAGING_DIR)
	@cp -r $(@D)/* $(MALI_450_STAGING_DIR)
endef

define MALI_450_INSTALL_TARGET_CMDS
	@mkdir -p $(MALI_450_TARGET_DIR)
	@cp -r $(@D)/* $(MALI_450_TARGET_DIR)
endef

$(eval $(generic-package))
