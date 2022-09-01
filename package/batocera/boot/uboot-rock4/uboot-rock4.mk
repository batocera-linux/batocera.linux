################################################################################
#
# uboot files for rock4
#
################################################################################
UBOOT_ROCK4_VERSION = 1c17801dc72cbc932ee6742aea25e4ba52ec6b2a
UBOOT_ROCK4_SITE = https://github.com/Multi-Retropie/rock4-uboot

define UBOOT_ROCK4_INSTALL_TARGET_CMDS
	cp $(@D)/rock4-*   $(BINARIES_DIR)/
endef

$(eval $(generic-package))
