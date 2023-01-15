################################################################################
#
# uboot-rk3588
#
################################################################################
UBOOT_RK3588_VERSION = e8b6ae108b89256b6781195690b47a6ca0de6c95
UBOOT_RK3588_SITE = https://github.com/stvhay/uboot-rk3588.git
UBOOT_RK3588_SITE_METHOD=git

define UBOOT_RK3588_INSTALL_TARGET_CMDS
	mkdir -p   $(BINARIES_DIR)/rock5b/
	cp $(@D)/* $(BINARIES_DIR)/rock5b/
endef

$(eval $(generic-package))
