################################################################################
#
# ayn-platform
#
################################################################################
# Version: Commits on Apr 16, 2024
AYN_PLATFORM_VERSION = 62032caddc25920f1f8ef256808d5a0cfc252f39
AYN_PLATFORM_SITE = $(call github,ShadowBlip,ayn-platform,$(AYN_PLATFORM_VERSION))
AYN_PLATFORM_LICENSE = GPL-3.0
AYN_PLATFORM_LICENSE_FILES = LICENSE

AYN_PLATFORM_MODULE_MAKE_OPTS = \
	CONFIG_AYN_PLATFORM=m \
	USER_EXTRA_CFLAGS="-DCONFIG_$(call qstrip,$(BR2_ENDIAN))_ENDIAN \
		-Wno-error"

$(eval $(kernel-module))
$(eval $(generic-package))
