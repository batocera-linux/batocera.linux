################################################################################
#
# recalbox-manager
#
################################################################################
RECALBOX_MANAGER_VERSION = 0.9.0 #6103f9bcee424294cc538c8efa84d90e831b45d1
RECALBOX_MANAGER_SITE = $(call github,sveetch,recalbox-manager,$(RECALBOX_MANAGER_VERSION))
RECALBOX_MANAGER_DEPENDENCIES = python

define RECALBOX-MANAGER_BUILD_CMDS
    $(MAKE) CC="$(TARGET_CC)" LD="$(TARGET_LD)" -C $(@D) all
endef

define RECALBOX-MANAGER_INSTALL_TARGET_CMDS
    $(INSTALL) -D $(@D)/* $(TARGET_DIR)/usr/recalbox-manager
endef

$(eval $(generic-package))
