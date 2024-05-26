################################################################################
#
# chromebook-ucm-conf
#
################################################################################
# Version: Commits on Feb 8, 2024 (use Standalone branch)
CHROMEBOOK_UCM_CONF_VERSION = 6b395ae73ac63407d8a9892fe1290f191eb0315b
CHROMEBOOK_UCM_CONF_SITE = $(call github,WeirdTreeThing,alsa-ucm-conf-cros,$(CHROMEBOOK_UCM_CONF_VERSION))
CHROMEBOOK_UCM_CONF_LICENSE = BSD-3-Clause
CHROMEBOOK_UCM_CONF_LICENSE_FILES = LICENSE

# we need the alsa-ucm dependencies first
CHROMEBOOK_UCM_CONF_DEPENDENCIES += alsa-ucm-conf alsa-utils
CHROMEBOOK_UCM_CONF_DEPENDENCIES += alllinuxfirmwares sound-open-firmware

define CHROMEBOOK_UCM_CONF_INSTALL_TARGET_CMDS
    rsync -arv $(@D)/ucm2/* $(TARGET_DIR)/usr/share/alsa/ucm2/
endef

$(eval $(generic-package))
