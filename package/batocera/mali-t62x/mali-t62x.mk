################################################################################
#
# mali-t62x
# http://malideveloper.arm.com/resources/drivers/arm-mali-midgard-gpu-user-space-drivers
#
################################################################################

MALI_T62X_VERSION = r7p0-02rel0
MALI_T62X_SOURCE = mali-t62x_r7p0-02rel0_linux_1+fbdev.tar.gz
MALI_T62X_SITE = http://malideveloper.arm.com/downloads/drivers/binary/r7p0-02rel0

MALI_T62X_INSTALL_STAGING = YES
MALI_T62X_DEPENDENCIES = mali-opengles-sdk
MALI_T62X_PROVIDES = libegl libgles

MALI_T62X_TARGET_DIR=$(TARGET_DIR)/usr/lib
MALI_T62X_STAGING_DIR=$(STAGING_DIR)/usr/lib

define MALI_T62X_INSTALL_STAGING_CMDS
	@mkdir -p $(MALI_T62X_STAGING_DIR)
	@cp -r $(@D)/* $(MALI_T62X_STAGING_DIR)
endef

define MALI_T62X_INSTALL_TARGET_CMDS
	@mkdir -p $(MALI_T62X_TARGET_DIR)
	@cp -r $(@D)/* $(MALI_T62X_TARGET_DIR)
endef

$(eval $(generic-package))
