################################################################################
#
# uboot files for RK3399
#
################################################################################
UBOOT_RK3399_VERSION = 468d5eef78d32241d2b045f3fc26e6280aacfbab
UBOOT_RK3399_SITE = https://github.com/batocera-linux/uboot-rk3399.git
UBOOT_RK3399_SITE_METHOD=git

define UBOOT_RK3399_INSTALL_TARGET_CMDS
	mkdir -p   $(BINARIES_DIR)/rk3399/
	cp $(@D)/* $(BINARIES_DIR)/rk3399/
endef

$(eval $(generic-package))
