################################################################################
#
# ayn-platform
#
################################################################################
# Version: Commits on Jul 17, 2024
AYN_PLATFORM_VERSION = ca662c4b3df4a2c69e7a81e09a5753bdf11d1594
AYN_PLATFORM_SITE = $(call github,ShadowBlip,ayn-platform,$(AYN_PLATFORM_VERSION))
AYN_PLATFORM_LICENSE = GPL-3.0
AYN_PLATFORM_LICENSE_FILES = LICENSE

AYN_PLATFORM_MODULE_MAKE_OPTS = \
	CONFIG_AYN_PLATFORM=m \
	USER_EXTRA_CFLAGS="-DCONFIG_$(call qstrip,$(BR2_ENDIAN))_ENDIAN \
		-Wno-error"

$(eval $(kernel-module))
$(eval $(generic-package))
