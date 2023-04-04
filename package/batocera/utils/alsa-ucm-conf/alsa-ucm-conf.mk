################################################################################
#
# alsa-ucm-conf
#
################################################################################
# Version.: Commits on Mar 20, 2023
ALSA_UCM_CONF_VERSION = f5d3c381e4471fb90601c4ecd1d3cf72874b2b27
ALSA_UCM_CONF_SITE = $(call github,alsa-project,alsa-ucm-conf,$(ALSA_UCM_CONF_VERSION))
ALSA_UCM_CONF_LICENSE = BSD-3-Clause
ALSA_UCM_CONF_LICENSE_FILES = LICENSE

define ALSA_UCM_CONF_INSTALL_TARGET_CMDS
	rsync -arv $(@D)/ucm* $(TARGET_DIR)/usr/share/alsa/
endef

$(eval $(generic-package))
