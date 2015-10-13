################################################################################
#
# recalbox-manager
#
################################################################################
RECALBOX_MANAGER_VERSION = 1.0.0 #0.8.4 #0.9.0 #6103f9bcee424294cc538c8efa84d90e831b45d1
RECALBOX_MANAGER_SITE = $(call github,sveetch,recalbox-manager,$(RECALBOX_MANAGER_VERSION))
RECALBOX_MANAGER_DEPENDENCIES = python python-psutil python-django python-autobreadcrumbs

#define RECALBOX_MANAGER_BUILD_CMDS
#    $(MAKE) CC="$(TARGET_CC)" LD="$(TARGET_LD)" -C $(@D) install
#endef

define RECALBOX_MANAGER_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/usr/recalbox-manager
	cp -r $(@D)/* $(TARGET_DIR)/usr/recalbox-manager
	$(TARGET_DIR)/bin/python $(TARGET_DIR)/usr/recalbox-manager/manage.py migrate
	#$(INSTALL) -D $(@D)/* $(TARGET_DIR)/usr/recalbox-manager
endef

define RECALBOX_MANAGER_INSTALL_INIT_SYSV
	$(INSTALL) -m 0755 -D package/recalbox-manager/script/S94manager $(TARGET_DIR)/etc/init.d/S94manager
endef


$(eval $(generic-package))
