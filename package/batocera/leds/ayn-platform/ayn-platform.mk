################################################################################
#
# ayn-platform
#
################################################################################
# Version: Commits on Mar 15, 2025
AYN_PLATFORM_VERSION = 9813128ddac097f8e11a92d64b33de7b70154989
AYN_PLATFORM_SITE = $(call github,ShadowBlip,ayn-platform,$(AYN_PLATFORM_VERSION))
AYN_PLATFORM_LICENSE = GPL-3.0
AYN_PLATFORM_LICENSE_FILES = LICENSE

AYN_PLATFORM_MODULE_MAKE_OPTS = \
	CONFIG_AYN_PLATFORM=m \
	USER_EXTRA_CFLAGS="-DCONFIG_$(call qstrip,$(BR2_ENDIAN))_ENDIAN \
		-Wno-error"

$(eval $(kernel-module))
$(eval $(generic-package))
