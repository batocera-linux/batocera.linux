################################################################################
#
# RetroLX meson64 (Amlogic S9xx) kernel package
#
################################################################################
KERNEL_MESON64_VERSION = 5.10.46
KERNEL_MESON64_SITE = https://github.com/RetroLX/kernel-meson64.git
KERNEL_MESON64_SITE_METHOD = git

define KERNEL_MESON64_INSTALL_TARGET_CMDS
	cp $(@D)/*      $(BINARIES_DIR)/
endef

$(eval $(generic-package))
