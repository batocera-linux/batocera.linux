################################################################################
#
# ayaneo-platform
#
################################################################################
# Version: Commits on Apr 15, 2024
AYANEO_PLATFORM_VERSION = 1b48cb070b1fb8a0245115ebe2d29c5811ae3f67
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
