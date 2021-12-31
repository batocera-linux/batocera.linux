################################################################################
#
# mali-midgard-module
#
################################################################################
# Version.: Commits on Nov 6, 2021
MALI_MIDGARD_MODULE_VERSION = 4d72a50cd76e2cdeef25fec113e3f6b3396f6e3c
MALI_MIDGARD_MODULE_SITE = $(call github,LibreELEC,mali-midgard,$(MALI_MIDGARD_MODULE_VERSION))

MALI_MIDGARD_MODULE_MODULE_MAKE_OPTS = \
	CONFIG_MALI_MIDGARD=m \
	CONFIG_MALI_PLATFORM_NAME="devicetree" \
	CONFIG_MALI_PLATFORM_POWER_DOWN_ONLY=y \
	KVER=$(LINUX_VERSION_PROBED) \
	KSRC=$(LINUX_DIR) \
		NOSTDINC_FLAGS=-I$(@D)/product/kernel/include

MALI_MIDGARD_MODULE_MODULE_SUBDIRS = driver/product/kernel/drivers/gpu/arm

$(eval $(kernel-module))
$(eval $(generic-package))




