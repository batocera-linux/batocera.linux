################################################################################
#
# seekwave-swt6621s
#
################################################################################

# Branch: kickpi-k3b-sdio-uart, Commit date: Jul 16, 2026
SEEKWAVE_SWT6621S_VERSION = b1b15016119cb21965fc64dd374e42f46f011bb4
SEEKWAVE_SWT6621S_SITE = $(call github,retro98boy,seekwave-swt6621s,$(SEEKWAVE_SWT6621S_VERSION))
SEEKWAVE_SWT6621S_LICENSE = GPL-2.0

SEEKWAVE_SWT6621S_MODULE_MAKE_OPTS = \
	CONFIG_SEEKWAVE_BSP_DRIVERS=m \
	CONFIG_SKW_NO_CONFIG=y \
	CONFIG_SKW_SDIOHAL=m \
	CONFIG_WLAN_VENDOR_SWT6621S=m \
	CONFIG_SKW_BT=m \
	CONFIG_SWT6621S_LOG_DEBUG=y

$(eval $(kernel-module))
$(eval $(generic-package))
