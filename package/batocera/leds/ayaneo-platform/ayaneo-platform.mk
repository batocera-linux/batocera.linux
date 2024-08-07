################################################################################
#
# ayaneo-platform
#
################################################################################
# Version: Commits on Jul 17, 2024
AYANEO_PLATFORM_VERSION = f29a4179d49b97a1035e379deca8bc53ba34f3ee
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
