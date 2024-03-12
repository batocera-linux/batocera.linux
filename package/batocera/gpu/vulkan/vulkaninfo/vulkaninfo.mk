################################################################################
#
# vulkaninfo
#
################################################################################

VULKANINFO_VERSION = 1.0
#VULKANINFO_SITE = 
VULKANINFO_SOURCE =

define VULKANINFO_INSTALL_TARGET_CMDS
	$(INSTALL) -D -m 0755 \
	    $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/gpu/vulkan/vulkaninfo/S55vulkaninfo \
	    $(TARGET_DIR)/etc/init.d/S55vulkaninfo
endef

$(eval $(generic-package))
