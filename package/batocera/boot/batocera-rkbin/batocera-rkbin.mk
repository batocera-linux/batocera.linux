################################################################################
#
# batocera-rkbin
#
################################################################################

BATOCERA_RKBIN_VERSION = 63c5815b8dda8e3bd60852cc4ac3dbe3c35c3038
BATOCERA_RKBIN_SITE = https://github.com/retro98boy/batocera-rkbin.git
BATOCERA_RKBIN_SITE_METHOD = git
BATOCERA_RKBIN_LICENSE = PROPRIETARY
BATOCERA_RKBIN_INSTALL_IMAGES = YES
BATOCERA_RKBIN_IMAGES_DIR = $(BINARIES_DIR)/batocera-rkbin

define BATOCERA_RKBIN_INSTALL_IMAGES_CMDS
	mkdir -p $(BATOCERA_RKBIN_IMAGES_DIR)
	cp -a $(@D)/bin $(@D)/tools $(BATOCERA_RKBIN_IMAGES_DIR)/
endef

$(eval $(generic-package))
