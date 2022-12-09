################################################################################
#
# firmware-orangepi
#
################################################################################
# Version.: Commits on Nov 24, 2022
FIRMWARE_ORANGEPI_VERSION = 44e2dfea2e1e6b1af6900b33246b424760b756c3
FIRMWARE_ORANGEPI_SITE = $(call github,orangepi-xunlong,firmware,$(FIRMWARE_ORANGEPI_VERSION))
FIRMWARE_ORANGEPI_DEPENDENCIES = alllinuxfirmwares

FIRMWARE_ORANGEPI_TARGET_DIR=$(TARGET_DIR)/lib/firmware

define FIRMWARE_ORANGEPI_INSTALL_TARGET_CMDS
	cp -r $(@D)/* $(FIRMWARE_ORANGEPI_TARGET_DIR)
endef

$(eval $(generic-package))
