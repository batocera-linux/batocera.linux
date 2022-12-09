################################################################################
#
# uboot files for rock4
#
################################################################################
UBOOT_ROCK4_VERSION = 1c17801dc72cbc932ee6742aea25e4ba52ec6b2a
UBOOT_ROCK4_SITE = https://github.com/Multi-Retropie/rock4-uboot
UBOOT_ROCK4_SITE_METHOD=git

define UBOOT_ROCK4_INSTALL_TARGET_CMDS
	mkdir -p   $(BINARIES_DIR)/rockpi4/
	cp $(@D)/rock4-*   $(BINARIES_DIR)/rockpi4/
endef

$(eval $(generic-package))
