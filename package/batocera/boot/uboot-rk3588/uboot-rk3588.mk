################################################################################
#
# uboot-rk3588
#
################################################################################

UBOOT_RK3588_VERSION = e1bb28dd5be8e347096be7b0ea4e64716d054268
UBOOT_RK3588_SITE = $(call github,stvhay,u-boot,$(UBOOT_RK3588_VERSION))
UBOOT_RK3588_LICENSE = GPL + Rockchip Proprietary (Extra Downloads)

define UBOOT_RK3588_BUILD_CMDS
	@echo "---- See github repository build.sh for build instructions. -----"
endef

define UBOOT_RK3588_INSTALL_TARGET_CMDS
	cp -rv $(@D)/staging/* $(BINARIES_DIR)
endef

$(eval $(generic-package))
