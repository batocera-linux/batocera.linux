################################################################################
#
# bigpemu
#
################################################################################

BIGPEMU_VERSION = v121
BIGPEMU_SOURCE = BigPEmu_Linux64_$(BIGPEMU_VERSION).tar.gz
BIGPEMU_SITE = https://www.richwhitehouse.com/jaguar/builds
BIGPEMU_EMULATOR_INFO = bigpemu.emulator.yml

define BIGPEMU_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/usr/bigpemu
	cp -pr $(@D)/* $(TARGET_DIR)/usr/bigpemu/
endef

$(eval $(generic-package))
$(eval $(emulator-info-package))