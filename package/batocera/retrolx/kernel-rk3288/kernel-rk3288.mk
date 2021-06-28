################################################################################
#
# RetroLX Rockchip RK3288 kernel package
#
################################################################################
KERNEL_RK3288_VERSION = 5.10.46
KERNEL_RK3288_SITE = https://github.com/RetroLX/kernel-rk3288.git
KERNEL_RK3288_SITE_METHOD = git

define KERNEL_RK3288_INSTALL_TARGET_CMDS
	cp $(@D)/*      $(BINARIES_DIR)/
endef

$(eval $(generic-package))
