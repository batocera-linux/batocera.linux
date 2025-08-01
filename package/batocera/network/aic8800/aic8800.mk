################################################################################
#
# aic8800
#
################################################################################
# Version: Commits on Jul 22, 2025
AIC8800_VERSION = dd2afa18bc47dfde591ee981b57bd7b22d017a0d
AIC8800_SITE = $(call github,radxa-pkg,aic8800,$(AIC8800_VERSION))
AIC8800_LICENSE = GPL-3.0
AIC8800_LICENSE_FILES = LICENSE

# build SDIO only
AIC8800_MODULE_SUBDIRS = src/SDIO/driver_fw/driver/aic8800

# set configs to be sure
AIC8800_MODULE_MAKE_OPTS = \
	CONFIG_AIC_WLAN_SUPPORT=y \
	CONFIG_AIC_FW_PATH="/lib/firmware/aic8800d80/" \
	CONFIG_AIC8800_WLAN_SUPPORT=m \
	CONFIG_AIC8800_BTLPM_SUPPORT=m \
	USER_EXTRA_CFLAGS="-DCONFIG_$(call qstrip,$(BR2_ENDIAN))_ENDIAN \
		-Wno-error"

# only copy firmware for the SDIO for now
define AIC8800_FIRMWARE_ETC
    mkdir -p $(TARGET_DIR)/lib/firmware/aic8800d80
	cp -f $(@D)/src/SDIO/driver_fw/fw/aic8800D80/* \
	    $(TARGET_DIR)/lib/firmware/aic8800d80
endef

AIC8800_POST_INSTALL_TARGET_HOOKS = AIC8800_FIRMWARE_ETC

$(eval $(kernel-module))
$(eval $(generic-package))
