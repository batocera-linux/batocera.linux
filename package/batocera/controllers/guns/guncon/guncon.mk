################################################################################
#
# guncon
#
################################################################################
GUNCON_VERSION = 4e959300f14b9ad364ea66dce6189c076de63a27
GUNCON_SITE = $(call github,Redemp,guncon2,$(GUNCON_VERSION))

define GUNCON_INSTALL_TARGET_CMDS
    $(INSTALL) -m 0644 -D $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/controllers/guns/guncon/99-guncon.rules $(TARGET_DIR)/etc/udev/rules.d/99-guncon.rules
    $(INSTALL) -m 0755 -D $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/controllers/guns/guncon/guncon-add      $(TARGET_DIR)/usr/bin/guncon-add
    $(INSTALL) -D -m 0755 $(@D)/guncon2_calibrate.sh $(TARGET_DIR)/usr/bin/guncon2_calibrate.sh
    $(INSTALL) -D -m 0755 $(@D)/calibrate.py $(TARGET_DIR)/usr/bin/calibrate.py
endef


$(eval $(kernel-module))
$(eval $(generic-package))
