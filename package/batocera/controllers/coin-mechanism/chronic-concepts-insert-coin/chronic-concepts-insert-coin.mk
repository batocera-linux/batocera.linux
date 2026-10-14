################################################################################
#
# chronic-concepts-insert-coin
#
################################################################################
CHRONIC_CONCEPTS_INSERT_COIN_VERSION = 1.0
CHRONIC_CONCEPTS_INSERT_COIN_SOURCE=

define CHRONIC_CONCEPTS_INSERT_COIN_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/99-Chronic_Concepts_Insert_Coin_Cube.rules $(TARGET_DIR)/etc/udev/rules.d/
	$(INSTALL) -D $(@D)/Chronic_Concepts_Insert_Coin_Cube.mapping $(TARGET_DIR)/usr/share/hotkeygen/
endef

$(eval $(generic-package))
