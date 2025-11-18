################################################################################
#
# aic8800
#
################################################################################
# Version: Commits on Oct 25, 2025
AIC8800_VERSION = 451a1c8f14dad821034017ccb902eaf0a2b8c2ee
AIC8800_SITE = $(call github,radxa-pkg,aic8800,$(AIC8800_VERSION))
AIC8800_LICENSE = GPL-3.0
AIC8800_LICENSE_FILES = LICENSE

ifeq ($(BR2_PACKAGE_AIC8800_SDIO),y)
AIC8800_MODULE_SUBDIRS = src/SDIO/driver_fw/driver/aic8800
endif

ifeq ($(BR2_PACKAGE_AIC8800_USB),y)
AIC8800_MODULE_SUBDIRS += src/USB/driver_fw/drivers/aic8800 src/USB/driver_fw/drivers/aic_btusb   
endif

# set configs to be sure
AIC8800_MODULE_MAKE_OPTS = \
	CONFIG_AIC_WLAN_SUPPORT=y \
	CONFIG_AIC_FW_PATH="/lib/firmware/aic8800_fw" \
	CONFIG_AIC8800_WLAN_SUPPORT=m \
	CONFIG_AIC8800_BTLPM_SUPPORT=m \
	USER_EXTRA_CFLAGS="-DCONFIG_$(call qstrip,$(BR2_ENDIAN))_ENDIAN \
		-Wno-error"

define AIC8800_DEBIAN_PATCHES
	@$(call MESSAGE,"Patching AIC8800 with debian patches")
	$(APPLY_PATCHES) $(@D) $(dir $(@D)/debian/patches/series)
endef

# Rock 5c uses aic8800D80 & CoolPi 4b uses aic8800
define AIC8800_FIRMWARE_ETC_SDIO
    mkdir -p $(TARGET_DIR)/lib/firmware/aic8800_fw/SDIO
	cp -rf $(@D)/src/SDIO/driver_fw/fw/aic8800 \
	    $(TARGET_DIR)/lib/firmware/aic8800_fw/SDIO
	cp -rf $(@D)/src/SDIO/driver_fw/fw/aic8800D80 \
	    $(TARGET_DIR)/lib/firmware/aic8800_fw/SDIO
	cp -rf $(@D)/src/SDIO/driver_fw/fw/aic8800D80X2 \
	    $(TARGET_DIR)/lib/firmware/aic8800_fw/SDIO
	cp -rf $(@D)/src/SDIO/driver_fw/fw/aic8800DC \
	    $(TARGET_DIR)/lib/firmware/aic8800_fw/SDIO
	# remove orangepi firmware duplication here...
	rm -rf $(TARGET_DIR)/lib/firmware/aic8800d80
endef

define AIC8800_FIRMWARE_ETC_USB
    mkdir -p $(TARGET_DIR)/lib/firmware/aic8800_fw/USB
	cp -rf $(@D)/src/USB/driver_fw/fw/aic8800 \
	    $(TARGET_DIR)/lib/firmware/aic8800_fw/USB
	cp -rf $(@D)/src/USB/driver_fw/fw/aic8800D80 \
	    $(TARGET_DIR)/lib/firmware/aic8800_fw/USB
	cp -rf $(@D)/src/USB/driver_fw/fw/aic8800D80X2 \
	    $(TARGET_DIR)/lib/firmware/aic8800_fw/USB
	cp -rf $(@D)/src/USB/driver_fw/fw/aic8800DC \
	    $(TARGET_DIR)/lib/firmware/aic8800_fw/USB
endef

AIC8800_POST_PATCH_HOOKS = AIC8800_DEBIAN_PATCHES

ifeq ($(BR2_PACKAGE_AIC8800_SDIO),y)
AIC8800_POST_INSTALL_TARGET_HOOKS = AIC8800_FIRMWARE_ETC_SDIO
endif
ifeq ($(BR2_PACKAGE_AIC8800_USB),y)
AIC8800_POST_INSTALL_TARGET_HOOKS += AIC8800_FIRMWARE_ETC_USB
endif

$(eval $(kernel-module))
$(eval $(generic-package))
