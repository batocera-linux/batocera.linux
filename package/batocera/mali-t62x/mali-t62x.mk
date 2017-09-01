################################################################################
#
# mali-t62x
# http://malideveloper.arm.com/resources/drivers/arm-mali-midgard-gpu-user-space-drivers
#
################################################################################

MALI_T62X_VERSION = malit62xr12p004rel0linux1fbdev
MALI_T62X_SOURCE = malit62xr12p004rel0linux1fbdev.tar.gz
MALI_T62X_SITE = https://developer.arm.com/-/media/Files/downloads/mali-drivers/user-space/odroid-xu3

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
