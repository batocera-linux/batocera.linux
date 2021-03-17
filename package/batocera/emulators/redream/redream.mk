################################################################################
#
# redream
#
################################################################################

REDREAM_VERSION = 1.5.0-785-g4e66e91
REDREAM_SOURCE = redream.x86_64-linux-v$(REDREAM_VERSION).tar.gz
REDREAM_SITE = https://github.com/liberodark/redream-repo/releases/download/1.0
# REDREAM_SITE = https://redream.io/download
# temporarly link to a private repo untile the stable is realeased

define REDREAM_EXTRACT_CMDS
	mkdir -p $(@D)/target && cd $(@D)/target && tar xf $(DL_DIR)/$(REDREAM_DL_SUBDIR)/$(REDREAM_SOURCE)
endef

define REDREAM_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/usr/bin
	mkdir -p $(TARGET_DIR)/usr/share/evmapy

	cp -pr $(@D)/target/redream $(TARGET_DIR)/usr/bin/redream

	# evmap config
	mkdir -p $(TARGET_DIR)/usr/share/evmapy
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulators/redream/dreamcast.redream.keys $(TARGET_DIR)/usr/share/evmapy
endef

$(eval $(generic-package))
