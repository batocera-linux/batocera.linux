################################################################################
#
# gun4ir-guns
#
################################################################################
GUN4IR_GUNS_VERSION = 1
GUN4IR_GUNS_LICENSE = GPL
GUN4IR_GUNS_SOURCE=

define GUN4IR_GUNS_INSTALL_TARGET_CMDS
	$(INSTALL) -m 0644 -D $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/controllers/gun4ir-guns/99-gun4ir.rules $(TARGET_DIR)/etc/udev/rules.d/99-gun4ir.rules
endef

$(eval $(generic-package))
