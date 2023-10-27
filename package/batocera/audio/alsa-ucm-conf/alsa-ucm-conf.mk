################################################################################
#
# alsa-ucm-conf
#
################################################################################

ALSA_UCM_CONF_VERSION = v1.2.10
ALSA_UCM_CONF_SITE = $(call github,alsa-project,alsa-ucm-conf,$(ALSA_UCM_CONF_VERSION))
ALSA_UCM_CONF_LICENSE = BSD-3-Clause
ALSA_UCM_CONF_LICENSE_FILES = LICENSE

define ALSA_UCM_CONF_INSTALL_TARGET_CMDS
	rsync -arv $(@D)/ucm* $(TARGET_DIR)/usr/share/alsa/ --exclude acp5x
	# exclude the acp5x specific to the steam deck. it causes audio Source to DSP after standby.
	# we have our own file in batocera-audio packages - todo : analyze to get the best of the two files
endef

$(eval $(generic-package))
