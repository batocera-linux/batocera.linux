################################################################################
#
# rock960-blobs
#
################################################################################

ROCK960_BLOBS_VERSION = 338f4e8
ROCK960_BLOBS_SITE = https://github.com/Multi-Retropie/rock960-blobs.git
ROCK960_BLOBS_SITE_METHOD=git

define ROCK960_BLOBS_INSTALL_TARGET_CMDS
	cp $(@D)/idbspl.img $(BINARIES_DIR)/
	cp $(@D)/u-boot.itb $(BINARIES_DIR)/
endef

$(eval $(generic-package))
