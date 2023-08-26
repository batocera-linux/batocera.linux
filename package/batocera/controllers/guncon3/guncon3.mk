################################################################################
#
# guncon3
#
################################################################################
GUNCON3_VERSION = 0dfe0feaa2afc37a8a70f6cd0f6c803ee4d89f40
GUNCON3_SITE = $(call github,pcnimdock,guncon3_dkms,$(GUNCON3_VERSION))

GUNCON3_MODULE_SUBDIRS = src

define GUNCON3_INSTALL_TARGET_CMDS
    $(INSTALL) -m 0644 -D $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/controllers/guncon3/99-guncon3.rules $(TARGET_DIR)/etc/udev/rules.d/99-guncon3.rules
    $(INSTALL) -m 0755 -D $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/controllers/guncon3/guncon3-add      $(TARGET_DIR)/usr/bin/guncon3-add
endef

$(eval $(kernel-module))
$(eval $(generic-package))
