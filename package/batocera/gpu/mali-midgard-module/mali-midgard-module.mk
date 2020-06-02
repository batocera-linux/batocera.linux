################################################################################
#
# mali-midgard-module
#
################################################################################

MALI_MIDGARD_MODULE_VERSION = r29
MALI_MIDGARD_MODULE_SOURCE = TX041-SW-99002-$(MALI_MIDGARD_MODULE_VERSION)p0-01rel0.tar
MALI_MIDGARD_MODULE_SITE = https://armkeil.blob.core.windows.net/developer/Files/downloads/mali-drivers/kernel/mali-midgard-gpu

MALI_MIDGARD_MODULE_MODULE_MAKE_OPTS = \
	CONFIG_MALI_MIDGARD=m \
	CONFIG_MALI_PLATFORM_NAME="devicetree" \
	CONFIG_MALI_PLATFORM_POWER_DOWN_ONLY=y \
	KVER=$(LINUX_VERSION_PROBED) \
	KSRC=$(LINUX_DIR) \
		NOSTDINC_FLAGS=-I$(@D)/product/kernel/include

MALI_MIDGARD_MODULE_MODULE_SUBDIRS = product/kernel/drivers/gpu/arm

$(eval $(kernel-module))
$(eval $(generic-package))
