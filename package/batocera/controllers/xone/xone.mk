################################################################################
#
# xone
#
################################################################################

XONE_VERSION = bbf0dcc484c3f5611f4e375da43e0e0ef08f3d18
XONE_SITE = $(call github,medusalix,xone,$(XONE_VERSION))
XONE_DEPENDENCIES = host-libcurl host-cabextract libusb

define XONE_INSTALL_TARGET_CMDS
	$(INSTALL) -D -m 0644 $(@D)/install/modprobe.conf $(TARGET_DIR)/etc/modprobe.d/xone-blacklist.conf
	# copy firmware
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/controllers/xone/FW_ACC_00U.bin \
	$(TARGET_DIR)/lib/firmware/xow_dongle.bin
endef

$(eval $(kernel-module))
$(eval $(generic-package))
