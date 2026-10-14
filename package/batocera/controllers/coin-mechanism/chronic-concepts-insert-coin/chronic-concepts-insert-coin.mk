################################################################################
#
# chronic-concepts-insert-coin
#
################################################################################
CHRONIC_CONCEPTS_INSERT_COIN_VERSION = 1.0
CHRONIC_CONCEPTS_INSERT_COIN_SOURCE=

define CHRONIC_CONCEPTS_INSERT_COIN_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/etc/udev/rules.d
	mkdir -p $(TARGET_DIR)/usr/share/hotkeygen
	$(INSTALL) -m 755 $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/controllers/coin-mechanism/chronic-concepts-insert-coin/99-Chronic_Concepts_Insert_Coin_Cube.rules $(TARGET_DIR)/etc/udev/rules.d/
	$(INSTALL) -m 755 $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/controllers/coin-mechanism/chronic-concepts-insert-coin/Chronic_Concepts_Insert_Coin_Cube_Gen_2-c2d2-2727.mapping $(TARGET_DIR)/usr/share/hotkeygen/
endef

$(eval $(generic-package))
