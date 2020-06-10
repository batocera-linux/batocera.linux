################################################################################
#
# rock960-blobs
#
################################################################################

ROCK960_BLOBS_VERSION = 25a39c5
ROCK960_BLOBS_SITE = https://github.com/Multi-Retropie/rock960-blobs.git
ROCK960_BLOBS_SITE_METHOD=git

define ROCK960_BLOBS_INSTALL_TARGET_CMDS
	cp $(@D)/idbloader.img $(BINARIES_DIR)/
	cp $(@D)/trust.img     $(BINARIES_DIR)/
	cp $(@D)/uboot.img     $(BINARIES_DIR)/
endef

$(eval $(generic-package))
