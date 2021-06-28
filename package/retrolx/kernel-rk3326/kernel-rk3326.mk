################################################################################
#
# RetroLX Rockchip RK3326 kernel package
#
################################################################################
KERNEL_RK3326_VERSION = 5.10.46
KERNEL_RK3326_SITE = https://github.com/RetroLX/kernel-rk3326.git
KERNEL_RK3326_SITE_METHOD = git

define KERNEL_RK3326_INSTALL_TARGET_CMDS
	cp $(@D)/*      $(BINARIES_DIR)/
endef

$(eval $(generic-package))
