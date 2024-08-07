################################################################################
#
# aic8800
#
################################################################################
# Version: Commits on Jun 25, 2024
AIC8800_VERSION = ccba7fffed8554fe861bd631ff6f852d2d6eec39
AIC8800_SITE = $(call github,batocera-linux,aic8800,$(AIC8800_VERSION))
AIC8800_LICENSE = GPL-2.0
AIC8800_LICENSE_FILES = LICENSE

AIC8800_MODULE_MAKE_OPTS = \
	AIC_WLAN_SUPPORT=m \
	USER_EXTRA_CFLAGS="-DCONFIG_$(call qstrip,$(BR2_ENDIAN))_ENDIAN \
		-Wno-error"

# only copy firmware for the Rock 5c for now
define AIC8800_FIRMWARE_ETC
    mkdir -p $(TARGET_DIR)/lib/firmware/aic8800D80
	cp -f $(@D)/firmware/aic8800D80/* $(TARGET_DIR)/lib/firmware/aic8800D80
endef

AIC8800_POST_INSTALL_TARGET_HOOKS = AIC8800_FIRMWARE_ETC

$(eval $(kernel-module))
$(eval $(generic-package))
