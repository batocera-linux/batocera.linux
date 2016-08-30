################################################################################
#
# recalbox-manager
#
################################################################################
RECALBOX_MANAGER_VERSION = recalbox-4.1.x
RECALBOX_MANAGER_SITE = $(call github,sveetch,recalbox-manager,$(RECALBOX_MANAGER_VERSION))
RECALBOX_MANAGER_DEPENDENCIES = python python-psutil python-django python-autobreadcrumbs

define RECALBOX_MANAGER_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/usr/recalbox-manager
	cp -r $(@D)/* $(TARGET_DIR)/usr/recalbox-manager
	cp package/recalbox-manager/bd/db.sqlite3 $(TARGET_DIR)/usr/recalbox-manager
endef

$(eval $(generic-package))
