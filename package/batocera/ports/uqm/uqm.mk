################################################################################
#
# uqm
#
################################################################################

UQM_VERSION = d6583f2250e6046de0bcd20e18ba78e8620fb638
UQM_SITE = https://git.code.sf.net/p/sc2/uqm
UQM_SITE_METHOD = git
UQM_DEPENDENCIES = sdl2 libpng libvorbis libzip
UQM_SUBDIR = sc2

define UQM_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/usr/share/evmapy
	$(INSTALL) -m 0755 $(@D)/sc2/src/urquan -D $(TARGET_DIR)/usr/bin/urquan
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/ports/uqm/uqm.keys $(TARGET_DIR)/usr/share/evmapy
endef

$(eval $(cmake-package))
