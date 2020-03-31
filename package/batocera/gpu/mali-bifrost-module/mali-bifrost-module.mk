################################################################################
#
# mali-bifrost-module
#
################################################################################
# Version.: Commits on Feb 26, 2020
MALI_BIFROST_MODULE_VERSION = af7c8d8bcdedd792a8d101d3a11876bb8bcbe3da
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
