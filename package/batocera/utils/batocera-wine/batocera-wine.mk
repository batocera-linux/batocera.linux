################################################################################
#
# batocera wine
#
################################################################################

BATOCERA_WINE_VERSION = 1.2
BATOCERA_WINE_LICENSE = GPL
BATOCERA_WINE_SOURCE=

BATOCERA_WINE_SOURCE_PATH = \
    $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/utils/batocera-wine

define BATOCERA_WINE_INSTALL_TARGET_CMDS
	install -m 0755 $(BATOCERA_WINE_SOURCE_PATH)/batocera-wine \
	    $(TARGET_DIR)/usr/bin/batocera-wine
	install -m 0755 $(BATOCERA_WINE_SOURCE_PATH)/batocera-wine-runners \
	    $(TARGET_DIR)/usr/bin/batocera-wine-runners
	install -m 0755 $(BATOCERA_WINE_SOURCE_PATH)/bsod.py \
	    $(TARGET_DIR)/usr/bin/bsod-wine
	ln -fs /userdata/system/99-nvidia.conf $(TARGET_DIR)/etc/X11/xorg.conf.d/99-nvidia.conf

	mkdir -p $(TARGET_DIR)/usr/share/evmapy
	cp $(BATOCERA_WINE_SOURCE_PATH)/mugen.keys \
	    $(TARGET_DIR)/usr/share/evmapy
endef

$(eval $(generic-package))
