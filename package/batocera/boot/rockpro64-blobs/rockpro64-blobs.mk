################################################################################
#
# rockpro64-blobs
#
################################################################################

ROCKPRO64_BLOBS_VERSION = 2.0
ROCKPRO64_BLOBS_SITE = https://github.com/batocera-linux/rockpro64-blobs.git
ROCKPRO64_BLOBS_SITE_METHOD=git

define ROCKPRO64_BLOBS_INSTALL_TARGET_CMDS
	cp $(@D)/idbloader.img $(BINARIES_DIR)/
	cp $(@D)/trust.img     $(BINARIES_DIR)/
	cp $(@D)/uboot.img     $(BINARIES_DIR)/
endef

$(eval $(generic-package))
