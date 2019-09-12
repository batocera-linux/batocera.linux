################################################################################
#
# RetroFlag 
#
################################################################################
# Version.: Commits on May 18, 2018
RETROFLAG_VERSION = ac0b5a6718c543ce7f10bb70b829dc24d8534e9f
RETROFLAG_SITE = $(call github,RetroFlag,retroflag-picase,$(RETROFLAG_VERSION))

define RETROFLAG_INSTALL_TARGET_CMDS
	$(INSTALL) -D -m 0755 package/batocera/utils/retroflag/S95RetroFlag $(TARGET_DIR)/etc/init.d/S95RetroFlag
	$(INSTALL) -D -m 0755 $(@D)/recalbox_SafeShutdown.py $(TARGET_DIR)/usr/bin/retroflag_SafeShutdown.py
endef

$(eval $(generic-package))
