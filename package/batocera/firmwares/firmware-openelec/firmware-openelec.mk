################################################################################
#
# firmware-openelec
#
################################################################################

FIRMWARE_OPENELEC_VERSION = 0.0.51
FIRMWARE_OPENELEC_SOURCE = $(FIRMWARE_OPENELEC_VERSION).tar.bz2
FIRMWARE_OPENELEC_SITE = https://github.com/OpenELEC/dvb-firmware/archive/refs/tags/
FIRMWARE_OPENELEC_LICENSE_FILES = firmware/LICENSE.go7007 firmware/LICENSE.siano firmware/LICENSE.xc5000 firmware/LICENSE.dib0700 firmware/README.as102 firmware/license-end-user.txt firmware/license-oemihvisv.txt

FIRMWARE_OPENELEC_TARGET_DIR=$(TARGET_DIR)/lib/firmware

define FIRMWARE_OPENELEC_INSTALL_TARGET_CMDS
	mkdir -p $(FIRMWARE_OPENELEC_TARGET_DIR)
	mv $(@D)/firmware/README $(@D)/firmware/LICENSE.linuxtv_dvb
	cp -r $(@D)/firmware/* $(FIRMWARE_OPENELEC_TARGET_DIR)/
endef

$(eval $(generic-package))
