################################################################################
#
# uwe5622
#
################################################################################
# Version: Commits on Sep 13, 2026
UWE5622_VERSION = cc2835a3f935d5297e03cdce464c1785381a7b4d
UWE5622_SITE = $(call github,armbian,uwe5622,$(UWE5622_VERSION))

UWE5622_MODULE_MAKE_OPTS = \
    CONFIG_WLAN_UWE5622=m \
    CONFIG_TTY_OVERY_SDIO=m \
    CONFIG_AW_WIFI_DEVICE_UWE5622=y \
    KCFLAGS=-DCONFIG_AW_BIND_VERIFY

$(eval $(kernel-module))
$(eval $(generic-package))
