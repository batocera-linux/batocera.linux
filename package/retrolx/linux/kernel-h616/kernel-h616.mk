################################################################################
#
# RetroLX Allwinner H616 kernel package
#
################################################################################
KERNEL_H616_VERSION = main
KERNEL_H616_SITE = https://github.com/RetroLX/kernel-h616.git
KERNEL_H616_SITE_METHOD = git

define KERNEL_H616_INSTALL_TARGET_CMDS
	cp $(@D)/*      $(BINARIES_DIR)/
endef

$(eval $(generic-package))
