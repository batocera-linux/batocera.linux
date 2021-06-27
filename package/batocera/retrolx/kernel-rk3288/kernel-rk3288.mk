################################################################################
#
# RetroLX Rockchip RK3288 kernel package
#
################################################################################
KERNEL_RK3288_VERSION = 5.10.46
KERNEL_RK3288_SOURCE = kernel-rk3288-$(KERNEL_RK3288_VERSION).tar.gz
KERNEL_RK3288_SITE = https://github.com/RetroLX/kernel-rk3288/releases/download/$(KERNEL_RK3288_VERSION)

define KERNEL_RK3288_INSTALL_TARGET_CMDS
	#cp $(@D)/Image      $(BINARIES_DIR)/Image
	#cp $(@D)/modules    $(BINARIES_DIR)/modules
endef

$(eval $(generic-package))
