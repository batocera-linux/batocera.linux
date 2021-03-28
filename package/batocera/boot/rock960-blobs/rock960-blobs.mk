################################################################################
#
# rock960-blobs
#
################################################################################

ROCK960_BLOBS_VERSION = f1179c2171f53fa1de0da8467d42ecea9b8923db
ROCK960_BLOBS_SITE = https://github.com/Multi-Retropie/rock960-blobs.git
ROCK960_BLOBS_SITE_METHOD=git

define ROCK960_BLOBS_INSTALL_TARGET_CMDS
	cp $(@D)/idbloader.img $(BINARIES_DIR)/idbloader-rock960.img
	cp $(@D)/u-boot.itb $(BINARIES_DIR)/u-boot-rock960.itb
endef

$(eval $(generic-package))
