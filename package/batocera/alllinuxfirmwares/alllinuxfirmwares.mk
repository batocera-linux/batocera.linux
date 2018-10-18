################################################################################
#
# alllinuxfirmwares
#
################################################################################

ALLLINUXFIRMWARES_VERSION = 44d4fca9922a252a0bd81f6307bcc072a78da54a
ALLLINUXFIRMWARES_SITE = http://git.kernel.org/pub/scm/linux/kernel/git/firmware/linux-firmware.git
ALLLINUXFIRMWARES_SITE_METHOD = git

define ALLLINUXFIRMWARES_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/lib/firmware
	cp -pr $(@D)/* $(TARGET_DIR)/lib/firmware/
endef

$(eval $(generic-package))
