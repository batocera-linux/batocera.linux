################################################################################
#
# uwe5622
#
################################################################################
# Version: Commits on Jul 8, 2026
UWE5622_VERSION = 6088bdbaa9b31b355c807878450d21348eb4a8e3
UWE5622_SITE = $(call github,EvilOlaf,uwe5622,$(UWE5622_VERSION))

UWE5622_MODULE_MAKE_OPTS = \
    CONFIG_WLAN_UWE5622=m \
    CONFIG_TTY_OVERY_SDIO=m \
    USER_EXTRA_CFLAGS="-DCONFIG_$(call qstrip,$(BR2_ENDIAN))_ENDIAN -Wno-error"

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_H616),y)
UWE5622_MODULE_MAKE_OPTS += CONFIG_AW_WIFI_DEVICE_UWE5622=y
endif

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RK3399),y)
UWE5622_MODULE_MAKE_OPTS += CONFIG_RK_WIFI_DEVICE_UWE5622=y
endif

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RK3568),y)
UWE5622_MODULE_MAKE_OPTS += CONFIG_RK_WIFI_DEVICE_UWE5622=y
endif

$(eval $(kernel-module))
$(eval $(generic-package))
