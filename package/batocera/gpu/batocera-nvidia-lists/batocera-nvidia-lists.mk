################################################################################
#
# batocera-nvidia-lists
#
################################################################################
# Version: Commits on Aug 9, 2023
BATOCERA_NVIDIA_LISTS_VERSION = d3992a821caaf8aba189fac6890eb490286d7694
BATOCERA_NVIDIA_LISTS_SITE = $(call github,batocera-linux,nvidia-lists,$(BATOCERA_NVIDIA_LISTS_VERSION))
BATOCERA_NVIDIA_LISTS_LICENSE = GPL-3.0+
BATOCERA_NVIDIA_LISTS_LICENSE_FILES = LICENSE

define BATOCERA_NVIDIA_LISTS_INSTALL_TARGET_CMDS
    mkdir -p $(TARGET_DIR)/usr/share/nvidia
	cp -r $(@D)/*.list $(TARGET_DIR)/usr/share/nvidia
endef

$(eval $(generic-package))
