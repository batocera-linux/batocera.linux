################################################################################
#
# broadcom-wl
#
################################################################################

BROADCOM_WL_VERSION = 6_30_223_271
BROADCOM_WL_SOURCE = hybrid-v35_64-nodebug-pcoem-$(BROADCOM_WL_VERSION).tar.gz
BROADCOM_WL_SITE = https://docs.broadcom.com/docs-and-downloads/docs/linux_sta
BROADCOM_WL_LICENSE = Custom
BROADCOM_WL_LICENSE_FILES = LICENSE.TXT

define BROADCOM_WL_EXTRACT_CMDS
    tar -xf $(BROADCOM_WL_DL_DIR)/$(BROADCOM_WL_SOURCE) -C $(@D)
endef

define BROADCOM_WL_PATCH_MAKE
    sed -i 's/EXTRA_CFLAGS :=/EXTRA_CFLAGS := -Wno-date-time/g' $(@D)/Makefile
	sed -i -e '/BRCM_WLAN_IFNAME/s/eth/wlan/' $(@D)/src/wl/sys/wl_linux.c
endef

define BROADCOM_WL_BLACKLIST
    echo "blacklist wl" > $(TARGET_DIR)/etc/modprobe.d/blacklist-wl.conf
	cp -f $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/network/broadcom-wl/macbook-wifi.conf.in \
	    $(TARGET_DIR)/etc/modprobe.d/macbook-wifi.conf.disabled
endef

BROADCOM_WL_MODULE_MAKE_OPTS = \
	CONFIG_BROADCOM_WL=m \
	USER_EXTRA_CFLAGS="-DCONFIG_$(call qstrip,$(BR2_ENDIAN))_ENDIAN \
		-Wno-error"

BROADCOM_WL_PRE_CONFIGURE_HOOKS = BROADCOM_WL_PATCH_MAKE
BROADCOM_WL_POST_INSTALL_TARGET_HOOKS = BROADCOM_WL_BLACKLIST

$(eval $(kernel-module))
$(eval $(generic-package))
