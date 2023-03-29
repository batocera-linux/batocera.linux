################################################################################
#
# alsa-topology-conf
#
################################################################################

ALSA_TOPOLOGY_CONF_VERSION = v1.2.5.1
ALSA_TOPOLOGY_CONF_SITE = $(call github,alsa-project,alsa-topology-conf,$(ALSA_TOPOLOGY_CONF_VERSION))
ALSA_TOPOLOGY_CONF_LICENSE = BSD-3-Clause
ALSA_TOPOLOGY_CONF_LICENSE_FILES = LICENSE

define ALSA_TOPOLOGY_CONF_INSTALL_TARGET_CMDS
    mkdir -p $(TARGET_DIR)/usr/share/alsa
	rsync -arv $(@D)/topology/* $(TARGET_DIR)/usr/share/alsa/topology/
endef

$(eval $(generic-package))
