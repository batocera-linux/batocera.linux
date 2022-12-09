################################################################################
#
# swapit
#
################################################################################
# Version.: Commits on May 27, 2020
SWAPIT_VERSION = 1
SWAPIT_SOURCE =
SWAPIT_LICENSE = GPLv3+

define SWAPIT_INSTALL_TARGET_CMDS
	$(INSTALL) -m 0755 -D $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/core/swapit/S40swapit $(TARGET_DIR)/etc/init.d/S40swapit
endef

$(eval $(generic-package))
