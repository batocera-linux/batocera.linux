################################################################################
#
# mali-midgard-module
#
################################################################################
# Version.: Commits on Jan 10, 2022
MALI_MIDGARD_MODULE_VERSION = 2c2accf67356463ee661627b8705429256011dcb
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




