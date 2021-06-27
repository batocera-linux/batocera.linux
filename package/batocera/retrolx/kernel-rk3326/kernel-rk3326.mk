################################################################################
#
# RetroLX Rockchip RK3326 kernel package
#
################################################################################
KERNEL_RK3326_VERSION = 5.10.46
KERNEL_RK3326_SOURCE = kernel-rk3326-$(KERNEL_RK3326_VERSION).tar.gz
KERNEL_RK3326_SITE = https://github.com/RetroLX/kernel-rk3326/releases/download/$(KERNEL_RK3326_VERSION)

define KERNEL_RK3326_INSTALL_TARGET_CMDS
	#cp $(@D)/Image      $(BINARIES_DIR)/Image
	#cp $(@D)/modules    $(BINARIES_DIR)/modules
endef

$(eval $(generic-package))
