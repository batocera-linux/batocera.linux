################################################################################
#
# recalbox-manager
#
################################################################################
RECALBOX_MANAGER_VERSION = 0.9.0 #6103f9bcee424294cc538c8efa84d90e831b45d1
RECALBOX_MANAGER_SITE = $(call github,sveetch,recalbox-manager,$(RECALBOX_MANAGER_VERSION))
RECALBOX_MANAGER_DEPENDENCIES = python

define RECALBOX_MANAGER_BUILD_CMDS
    $(MAKE) CC="$(TARGET_CC)" LD="$(TARGET_LD)" -C $(@D) install
endef

define RECALBOX_MANAGER_INSTALL_TARGET_CMDS
    $(INSTALL) -D $(@D)/* $(TARGET_DIR)/usr/recalbox-manager
endef

define RECALBOX_INSTALL_INIT_SYSV
	$(INSTALL) -m 0755 -D package/recalbox-manager/S93manager $(TARGET_DIR)/etc/init.d/S93manager
    	$(INSTALL) -m 0755 -D package/recalbox-manager/start.sh  $(TARGET_DIR)/usr/recalbox-manager
endef


$(eval $(generic-package))
