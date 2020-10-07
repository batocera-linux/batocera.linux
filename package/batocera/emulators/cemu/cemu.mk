################################################################################
#
# Cemu
#
################################################################################

# version 1.21.2
CEMU_VERSION = 1.21.2
CEMU_SOURCE = cemu_$(CEMU_VERSION).zip
CEMU_SITE = https://cemu.info/releases

define CEMU_EXTRACT_CMDS
	mkdir -p $(@D) && cd $(@D) && unzip -x $(DL_DIR)/$(CEMU_DL_SUBDIR)/$(CEMU_SOURCE)
endef

define CEMU_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/usr/cemu/
	cp -prn $(@D)/cemu_$(CEMU_VERSION)/* $(TARGET_DIR)/usr/cemu/
endef

$(eval $(generic-package))
