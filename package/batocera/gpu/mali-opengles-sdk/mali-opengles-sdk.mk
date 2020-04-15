################################################################################
#
# mali-opengles-sdk
#
################################################################################

MALI_OPENGLES_SDK_VERSION = v2.4.4.ef7d5a_Linux_x64
MALI_OPENGLES_SDK_SOURCE = Mali_OpenGL_ES_SDK_v2.4.4.ef7d5a_Linux_x64.tar.gz
MALI_OPENGLES_SDK_SITE = https://developer.arm.com/-/media/Files/downloads/mali-sdk/v2.4.4

MALI_OPENGLES_SDK_INSTALL_STAGING = YES

MALI_OPENGLES_SDK_TARGET_DIR=$(TARGET_DIR)/usr/include
MALI_OPENGLES_SDK_STAGING_DIR=$(STAGING_DIR)/usr/include

define MALI_OPENGLES_SDK_INSTALL_STAGING_CMDS
	@mkdir -p $(MALI_OPENGLES_SDK_STAGING_DIR)
	@cp -r $(@D)/inc/* $(MALI_OPENGLES_SDK_STAGING_DIR)
	@cp -r $(@D)/simple_framework/inc/mali/* $(MALI_OPENGLES_SDK_STAGING_DIR)
	$(INSTALL) -D -m 0644 $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/gpu/mali-opengles-sdk/egl.pc \
		$(STAGING_DIR)/usr/lib/pkgconfig/egl.pc
	$(INSTALL) -D -m 0644 $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/gpu/mali-opengles-sdk/glesv2.pc \
		$(STAGING_DIR)/usr/lib/pkgconfig/glesv2.pc

endef

define MALI_OPENGLES_SDK_INSTALL_TARGET_CMDS
	@mkdir -p $(MALI_OPENGLES_SDK_TARGET_DIR)
	@cp -r $(@D)/inc/* $(MALI_OPENGLES_SDK_TARGET_DIR)
	@cp -r $(@D)/simple_framework/inc/mali/* $(MALI_OPENGLES_SDK_TARGET_DIR)
endef

$(eval $(generic-package))
