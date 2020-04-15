################################################################################
#
# alllinuxfirmwares
#
################################################################################
# Version from 2020-04-14 10:37 - amdgpu: update vega20 to the latest 19.50 firmware
ALLLINUXFIRMWARES_VERSION = 64dba0fedb22eae32f76dcd4534b3f416db178de
ALLLINUXFIRMWARES_SITE = http://git.kernel.org/pub/scm/linux/kernel/git/firmware/linux-firmware.git
ALLLINUXFIRMWARES_SITE_METHOD = git

define ALLLINUXFIRMWARES_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/lib/firmware
	cp -pr $(@D)/* $(TARGET_DIR)/lib/firmware/
endef

$(eval $(generic-package))
