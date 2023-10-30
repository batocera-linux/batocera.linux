################################################################################
#
# batocera-nvidia-lists
#
################################################################################
# Version: Commits on Oct 30, 2023
BATOCERA_NVIDIA_LISTS_VERSION = 8457138454764179bdec9585bc2e5fe4c8b7a1c8
BATOCERA_NVIDIA_LISTS_SITE = $(call github,batocera-linux,nvidia-lists,$(BATOCERA_NVIDIA_LISTS_VERSION))
BATOCERA_NVIDIA_LISTS_LICENSE = GPL-3.0+
BATOCERA_NVIDIA_LISTS_LICENSE_FILES = LICENSE

define BATOCERA_NVIDIA_LISTS_INSTALL_TARGET_CMDS
    mkdir -p $(TARGET_DIR)/usr/share/nvidia
	cp -r $(@D)/*.list $(TARGET_DIR)/usr/share/nvidia
endef

$(eval $(generic-package))
