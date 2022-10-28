################################################################################
#
# guncon
#
################################################################################
GUNCON_VERSION = e50b612d7c77879fb3df9402a3eaa88a5526fe3f
GUNCON_SITE = $(call github,beardypig,guncon2,$(GUNCON_VERSION))

define GUNCON_INSTALL_TARGET_CMDS
	$(INSTALL) -m 0644 -D $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/controllers/guncon/99-guncon.rules $(TARGET_DIR)/etc/udev/rules.d/99-guncon.rules
	$(INSTALL) -m 0755 -D $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/controllers/guncon/guncon-add      $(TARGET_DIR)/usr/bin/guncon-add
endef


$(eval $(kernel-module))
$(eval $(generic-package))
