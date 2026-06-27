################################################################################
#
# batocera-torrent
#
################################################################################

BATOCERA_TORRENT_VERSION = 1
BATOCERA_TORRENT_LICENSE = GPL
BATOCERA_TORRENT_SOURCE=

define BATOCERA_TORRENT_INSTALL_TARGET_CMDS
	$(INSTALL) -m 0755 -D $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/utils/batocera-torrent/batocera-upgrade-torrent $(TARGET_DIR)/usr/bin/batocera-upgrade-torrent
	$(INSTALL) -m 0755 -D $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/utils/batocera-torrent/batocera-torrent.service $(TARGET_DIR)/usr/share/batocera/services/batocera-torrent
endef

$(eval $(generic-package))
