################################################################################
#
# xone
#
################################################################################

# Workaround the need for Kernel 5.11 or greater with some boards
ifeq ($(BR2_PACKAGE_HOST_LINUX_HEADERS_CUSTOM_5_4)$(BR2_PACKAGE_HOST_LINUX_HEADERS_CUSTOM_5_10),y)
    XONE_VERSION = bbf0dcc484c3f5611f4e375da43e0e0ef08f3d18
else
    # Version: Commits on Oct 6, 2025
    XONE_VERSION = 3e53480d835eeb31049ef8a3b397f3180a1db9dc
endif

XONE_SITE = $(call github,dlundqvist,xone,$(XONE_VERSION))
XONE_DEPENDENCIES = host-libcurl host-cabextract libusb

define XONE_INSTALL_TARGET_CMDS
$(INSTALL) -D -m 0644 $(@D)/install/modprobe.conf \
    $(TARGET_DIR)/etc/modprobe.d/xone-blacklist.conf
# copy firmware
cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/controllers/pads/xone/FW_ACC_00U.bin \
    $(TARGET_DIR)/lib/firmware/xow_dongle.bin
# create symbolic link
ln -sf /lib/firmware/xow_dongle.bin \
    $(TARGET_DIR)/lib/firmware/xow_dongle_045e_02e6.bin
endef

$(eval $(kernel-module))
$(eval $(generic-package))
