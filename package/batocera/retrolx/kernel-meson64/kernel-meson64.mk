################################################################################
#
# RetroLX meson64 (Amlogic S9xx) kernel package
#
################################################################################
KERNEL_MESON64_VERSION = 5.10.46
KERNEL_MESON64_SOURCE = kernel-meson64-$(KERNEL_MESON64_VERSION).tar.gz
KERNEL_MESON64_SITE = https://github.com/RetroLX/kernel-meson64/releases/download/$(KERNEL_MESON64_VERSION)

define KERNEL_MESON64_INSTALL_TARGET_CMDS
	cp $(@D)/Image      $(BINARIES_DIR)/Image
	cp $(@D)/modules    $(BINARIES_DIR)/modules
endef

$(eval $(generic-package))
