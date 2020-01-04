################################################################################
#
# alllinuxfirmwares
#
################################################################################
# Version from 2019-04-29 08:50:27 -0500 - amdgpu: update vega20 to the latest 19.10 firmware
ALLLINUXFIRMWARES_VERSION = 20191215
ALLLINUXFIRMWARES_SITE = http://git.kernel.org/pub/scm/linux/kernel/git/firmware/linux-firmware.git
ALLLINUXFIRMWARES_SITE_METHOD = git

define ALLLINUXFIRMWARES_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/lib/firmware
	cp -pr $(@D)/* $(TARGET_DIR)/lib/firmware/
endef

$(eval $(generic-package))
