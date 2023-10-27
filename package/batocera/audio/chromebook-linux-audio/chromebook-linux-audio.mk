################################################################################
#
# chromebook-linux-audio
#
################################################################################
# Version: Commits on Oct 8, 2023
CHROMEBOOK_LINUX_AUDIO_VERSION = ae0ea9db863ab3de394697e84f2171ede8e1abca
CHROMEBOOK_LINUX_AUDIO_SITE = $(call github,WeirdTreeThing,chromebook-linux-audio,$(CHROMEBOOK_LINUX_AUDIO_VERSION))
CHROMEBOOK_LINUX_AUDIO_LICENSE = BSD-3-Clause
CHROMEBOOK_LINUX_AUDIO_LICENSE_FILES = LICENSE

# we need the alsa-ucm dependencies first
CHROMEBOOK_LINUX_AUDIO_DEPENDENCIES += alsa-ucm-conf alsa-utils
CHROMEBOOK_LINUX_AUDIO_DEPENDENCIES += alllinuxfirmwares sound-open-firmware
CHROMEBOOK_LINUX_AUDIO_DEPENDENCIES += chromebook-ucm-conf

define CHROMEBOOK_LINUX_AUDIO_INSTALL_TARGET_CMDS
    # AMD firmware
    mkdir -p $(TARGET_DIR)/lib/firmware/amd/sof/community
    mkdir -p $(TARGET_DIR)/lib/firmware/amd/sof-tplg
    rsync -arv $(@D)/conf/amd-sof/fw $(TARGET_DIR)/lib/firmware/amd/sof/community
    rsync -arv $(@D)/conf/amd-sof/tplg $(TARGET_DIR)/lib/firmware/amd/sof-tplg
endef

$(eval $(generic-package))
