################################################################################
#
# ayn-platform
#
################################################################################
# Version: Commits on Sep 22, 2023
AYN_PLATFORM_VERSION = 7f0c88d70be3e69c866e1284c9488c1044b4edce
AYN_PLATFORM_SITE = $(call github,ShadowBlip,ayn-platform,$(AYN_PLATFORM_VERSION))
AYN_PLATFORM_LICENSE = GPL-3.0
AYN_PLATFORM_LICENSE_FILES = LICENSE

AYN_PLATFORM_MODULE_MAKE_OPTS = \
	CONFIG_AYN_PLATFORM=m \
	USER_EXTRA_CFLAGS="-DCONFIG_$(call qstrip,$(BR2_ENDIAN))_ENDIAN \
		-Wno-error"

$(eval $(kernel-module))
$(eval $(generic-package))
