################################################################################
#
# RetroLX Rockchip RK3399 kernel package
#
################################################################################
KERNEL_RK3399_VERSION = 5.10.46
KERNEL_RK3399_SITE = https://github.com/RetroLX/kernel-rk3399.git
KERNEL_RK3399_SITE_METHOD = git

define KERNEL_RK3399_INSTALL_TARGET_CMDS
	cp $(@D)/*      $(BINARIES_DIR)/
endef

$(eval $(generic-package))
