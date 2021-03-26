################################################################################
#
# rockpro64-blobs
#
################################################################################

ROCKPRO64_BLOBS_VERSION = 2.0
ROCKPRO64_BLOBS_SITE = https://github.com/batocera-linux/rockpro64-blobs.git
ROCKPRO64_BLOBS_SITE_METHOD=git

define ROCKPRO64_BLOBS_INSTALL_TARGET_CMDS
	cp $(@D)/idbloader.img $(BINARIES_DIR)/idbloader-rockpro64.img
	cp $(@D)/trust.img     $(BINARIES_DIR)/trust-rockpro64.img
	cp $(@D)/uboot.img     $(BINARIES_DIR)/u-boot-rockpro64.bin
endef

$(eval $(generic-package))
