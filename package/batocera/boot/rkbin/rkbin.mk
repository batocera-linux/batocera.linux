################################################################################
#
# rkbin
#
################################################################################

RKBIN_VERSION = ecb4fcbe954edf38b3ae037d5de6d9f5bccf81f4
RKBIN_SITE = https://github.com/rockchip-linux/rkbin.git
RKBIN_SITE_METHOD = git
RKBIN_LICENSE = PROPRIETARY
RKBIN_INSTALL_IMAGES = YES

define RKBIN_INSTALL_IMAGES_CMDS
	mkdir -p $(BINARIES_DIR)/rkbin
	cp -a $(@D)/* $(BINARIES_DIR)/rkbin
endef

$(eval $(generic-package))
