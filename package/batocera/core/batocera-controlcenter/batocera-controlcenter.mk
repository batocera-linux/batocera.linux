################################################################################
#
# batocera-controlcenter
#
################################################################################
# Last commit on Nov 20, 2025
BATOCERA_CONTROLCENTER_VERSION = d6ff6c604b9b8d100ac6e06e6e96f307f5529c0e
BATOCERA_CONTROLCENTER_SITE = $(call github,lbrpdx,batocera-controlcenter,$(BATOCERA_CONTROLCENTER_VERSION))
BATOCERA_CONTROLCENTER_STE_METHOD = git
BATOCERA_CONTROLCENTER_LICENSE = GPL3
BATOCERA_CONTROLCENTER_INSTALL_STAGING = YES

BATOCERA_CONTROLCENTER_DEPENDENCIES = python3 python-evdev

BATOCERA_CONTROLCENTER_PATH = \
    $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/core/batocera-controlcenter

define BATOCERA_CONTROLCENTER_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/usr/bin
	mkdir -p $(TARGET_DIR)/usr/share/batocera/controlcenter
	install -m 0755 $(@D)/controlcenter.py  $(TARGET_DIR)/usr/share/batocera/controlcenter
	install -m 0755 $(@D)/style.css         $(TARGET_DIR)/usr/share/batocera/controlcenter
	install -m 0755 $(@D)/ui_core.py        $(TARGET_DIR)/usr/share/batocera/controlcenter
	install -m 0755 $(@D)/xml_utils.py      $(TARGET_DIR)/usr/share/batocera/controlcenter
	install -m 0755 $(@D)/shell.py          $(TARGET_DIR)/usr/share/batocera/controlcenter
	install -m 0755 $(@D)/refresh.py        $(TARGET_DIR)/usr/share/batocera/controlcenter
	cd $(TARGET_DIR)/usr/bin; ln -sf ../share/batocera/controlcenter/controlcenter.py \
	    ./batocera-controlcenter-app
	install -m 0755 $(BATOCERA_CONTROLCENTER_PATH)/batocera-controlcenter-toogle.sh \
	    $(TARGET_DIR)/usr/bin/batocera-controlcenter
	install -m 0755 $(BATOCERA_CONTROLCENTER_PATH)/controlcenter.xml \
	    $(TARGET_DIR)/usr/share/batocera/controlcenter
endef

$(eval $(generic-package))
