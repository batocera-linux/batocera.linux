################################################################################
#
# batocera-nvidia-lists
#
################################################################################
# Version: 515.48.07 production & 470.xx legacy lists
BATOCERA_NVIDIA_LISTS_VERSION = b44c8210aade1346b64693de90095e68ed059b31
BATOCERA_NVIDIA_LISTS_SITE = $(call github,batocera-linux,nvidia-lists,$(BATOCERA_NVIDIA_LISTS_VERSION))
BATOCERA_NVIDIA_LISTS_LICENSE = GPL-3.0+
BATOCERA_NVIDIA_LISTS_LICENSE_FILES = LICENSE

define BATOCERA_NVIDIA_LISTS_INSTALL_TARGET_CMDS
    mkdir -p $(TARGET_DIR)/usr/share/nvidia
	cp -r $(@D)/*.list $(TARGET_DIR)/usr/share/nvidia
endef

$(eval $(generic-package))
