################################################################################
#
# mali-bifrost-module
#
################################################################################
# Version: Commits on Jun 16, 2020
MALI_BIFROST_MODULE_VERSION = ae1fccae88e70e267135b1a766b414f735110fae
# MALI_BIFROST_MODULE_SITE = $(call github,LibreELEC,mali-bifrost,$(MALI_BIFROST_MODULE_VERSION))
MALI_BIFROST_MODULE_SITE = $(call github,batocera-linux,mali-bifrost,$(MALI_BIFROST_MODULE_VERSION))
# MALI_BIFROST_MODULE_OVERRIDE_SRCDIR = /sources/mali-bifrost

MALI_BIFROST_MODULE_MODULE_MAKE_OPTS = \
	CONFIG_MALI_MIDGARD=m \
	CONFIG_MALI_PLATFORM_NAME=meson \
	CONFIG_MALI_PLATFORM_POWER_DOWN_ONLY=y \
	KVER=$(LINUX_VERSION_PROBED) \
	KSRC=$(LINUX_DIR) \
		NOSTDINC_FLAGS=-I$(@D)/driver/product/kernel/include

MALI_BIFROST_MODULE_MODULE_SUBDIRS = driver/product/kernel/drivers/gpu/arm

$(eval $(kernel-module))
$(eval $(generic-package))
