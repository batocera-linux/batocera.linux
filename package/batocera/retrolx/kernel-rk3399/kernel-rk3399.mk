################################################################################
#
# RetroLX Rockchip RK3399 kernel package
#
################################################################################
KERNEL_RK3399_VERSION = 5.10.46
KERNEL_RK3399_SOURCE = kernel-rk3399-$(KERNEL_RK3399_VERSION).tar.gz
KERNEL_RK3399_SITE = https://github.com/RetroLX/kernel-rk3399/releases/download/$(KERNEL_RK3399_VERSION)

define KERNEL_RK3399_INSTALL_TARGET_CMDS
	#cp $(@D)/Image      $(BINARIES_DIR)/Image
	#cp $(@D)/modules    $(BINARIES_DIR)/modules
endef

$(eval $(generic-package))
