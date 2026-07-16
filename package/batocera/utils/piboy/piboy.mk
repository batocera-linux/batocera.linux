################################################################################
#
# piboy
#
################################################################################
# Version: Commits on Aug 7, 2022
PIBOY_VERSION = f30cea1a30e4e9ad8fcf3b7da48f2770b4ea3368
PIBOY_SITE = $(call github,hancock33,piboycontrols,$(PIBOY_VERSION))
PIBOY_DEPENDENCIES = linux

PIBOY_SRC = $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/utils/piboy

define PIBOY_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/usr/bin
	mkdir -p $(TARGET_DIR)/usr/share/piboy
	$(INSTALL) -D -m 0755 $(PIBOY_SRC)/piboy_fan_ctrl.py \
	    $(TARGET_DIR)/usr/bin/piboy_fan_ctrl.py
	$(INSTALL) -D -m 0755 $(PIBOY_SRC)/piboy_aud_ctrl.py \
	    $(TARGET_DIR)/usr/bin/piboy_aud_ctrl.py
	$(INSTALL) -D -m 0755 $(PIBOY_SRC)/piboy_power_ctrl.py \
	    $(TARGET_DIR)/usr/bin/piboy_power_ctrl.py
	cp -a $(PIBOY_SRC)/fan.ini \
	    $(TARGET_DIR)/usr/share/piboy/fan.ini
endef

$(eval $(kernel-module))
$(eval $(generic-package))
