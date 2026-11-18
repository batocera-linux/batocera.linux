################################################################################
#
# batocera-rkbin
#
################################################################################

BATOCERA_RKBIN_VERSION = 290e719c708f17f36b5a13a4c620e7cda0f1ac46
BATOCERA_RKBIN_SITE = https://github.com/batocera-linux/batocera-rkbin.git
BATOCERA_RKBIN_SITE_METHOD = git
BATOCERA_RKBIN_LICENSE = PROPRIETARY
BATOCERA_RKBIN_LICENSE_FILES = LICENSE
BATOCERA_RKBIN_DIR = $(HOST_DIR)/share/batocera-rkbin

define HOST_BATOCERA_RKBIN_INSTALL_CMDS
	mkdir -p $(BATOCERA_RKBIN_DIR)
	cp -a $(@D)/bin $(@D)/tools $(BATOCERA_RKBIN_DIR)/
endef

$(eval $(host-generic-package))
