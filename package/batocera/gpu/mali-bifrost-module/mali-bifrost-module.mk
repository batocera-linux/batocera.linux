################################################################################
#
# mali-bifrost-module
#
################################################################################

MALI_BIFROST_MODULE_VERSION = 61bf5319dfd266b72a96c9c2d518dbbde8514d66
MALI_BIFROST_MODULE_SITE = $(call github,LibreELEC,mali-bifrost,$(MALI_BIFROST_MODULE_VERSION))

MALI_BIFROST_MODULE_MODULE_MAKE_OPTS = \
	CONFIG_MALI_MIDGARD=m \
	CONFIG_MALI_PLATFORM_NAME=meson \
	CONFIG_MALI_PLATFORM_POWER_DOWN_ONLY=y \
	KVER=$(LINUX_VERSION_PROBED) \
	KSRC=$(LINUX_DIR) \
        NOSTDINC_FLAGS=-I$(@D)/product/kernel/include

MALI_BIFROST_MODULE_MODULE_SUBDIRS = driver/product/kernel/drivers/gpu/arm

$(eval $(kernel-module))
$(eval $(generic-package))
