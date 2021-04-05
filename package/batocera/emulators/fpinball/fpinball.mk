################################################################################
#
# Fpinball
#
################################################################################

FPINBALL_VERSION = v1.9.1.20101231
FPINBALL_SOURCE = fpinball-$(FPINBALL_VERSION).zip
FPINBALL_SITE = https://github.com/batocera-linux/fpinball/releases/download/$(FPINBALL_VERSION)

define FPINBALL_EXTRACT_CMDS
	mkdir -p $(@D) && cd $(@D) && unzip -x $(DL_DIR)/$(FPINBALL_DL_SUBDIR)/$(FPINBALL_SOURCE)
endef

define FPINBALL_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/usr/fpinball/
	cp -prn $(@D)/* $(TARGET_DIR)/usr/fpinball/

	#evmap config
	mkdir -p $(TARGET_DIR)/usr/share/evmapy
	cp -prn $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulators/fpinball/fpinball.keys $(TARGET_DIR)/usr/share/evmapy

endef

$(eval $(generic-package))
