################################################################################
#
# retroflag 
#
################################################################################
RETROFLAG_VERSION = b43b53dbc88696c42e47a634381a7ad94410f9a9
RETROFLAG_SITE = $(call github,RetroFlag,retroflag-picase,$(RETROFLAG_VERSION))

define RETROFLAG_INSTALL_TARGET_CMDS
	$(INSTALL) -D -m 0755 package/batocera/utils/retroflag/S95RetroFlag $(TARGET_DIR)/etc/init.d/S95RetroFlag
	$(INSTALL) -D -m 0755 $(@D)/recalbox_SafeShutdown.py $(TARGET_DIR)/usr/bin/retroflag_SafeShutdown.py
endef

$(eval $(generic-package))
