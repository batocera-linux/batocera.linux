################################################################################
#
# guncon3
#
################################################################################
GUNCON3_VERSION = 0dfe0feaa2afc37a8a70f6cd0f6c803ee4d89f40
GUNCON3_SITE = $(call github,pcnimdock,guncon3_dkms,$(GUNCON3_VERSION))

GUNCON3_MODULE_SUBDIRS = src

GUNCON3_SOURCE_PATH = $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/controllers/guns/guncon3

define GUNCON3_INSTALL_TARGET_CMDS
    $(INSTALL) -m 0644 -D $(GUNCON3_SOURCE_PATH)/99-guncon3.rules \
        $(TARGET_DIR)/etc/udev/rules.d/99-guncon3.rules
    $(INSTALL) -m 0755 -D $(GUNCON3_SOURCE_PATH)/guncon3-add \
        $(TARGET_DIR)/usr/bin/guncon3-add
    $(INSTALL) -m 0755 -D $(GUNCON3_SOURCE_PATH)/batocera-guncon3-calibrator \
        $(TARGET_DIR)/usr/bin/batocera-guncon3-calibrator
    $(INSTALL) -m 0755 -D $(GUNCON3_SOURCE_PATH)/batocera-guncon3-calibrator-daemon \
        $(TARGET_DIR)/usr/bin/batocera-guncon3-calibrator-daemon
endef

$(eval $(kernel-module))
$(eval $(generic-package))
