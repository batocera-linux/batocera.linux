################################################################################
#
# ayaneo-platform
#
################################################################################
# Version: Commits on May 22, 2025
AYANEO_PLATFORM_VERSION = 8ccdf707e7dd7a7c97307b078122b80e92a4ca62
AYANEO_PLATFORM_SITE = \
    $(call github,ShadowBlip,ayaneo-platform,$(AYANEO_PLATFORM_VERSION))
AYANEO_PLATFORM_LICENSE = GPL-3.0
AYANEO_PLATFORM_LICENSE_FILES = LICENSE

AYANEO_PLATFORM_MODULE_MAKE_OPTS = \
	CONFIG_AYANEO_PLATFORM=m \
	USER_EXTRA_CFLAGS="-DCONFIG_$(call qstrip,$(BR2_ENDIAN))_ENDIAN \
		-Wno-error"

$(eval $(kernel-module))
$(eval $(generic-package))
