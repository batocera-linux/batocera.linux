################################################################################
#
# rtw88
#
################################################################################
# Version: Commits on Jul 30, 2025
RTW88_VERSION = 549f33c361a2569733ba73e47d7e3986ca7e55d6
RTW88_SITE = $(call github,lwfinger,rtw88,$(RTW88_VERSION))

RTW88_MODULE_MAKE_OPTS = \
    CONFIG_RTW88=m \
    USER_EXTRA_CFLAGS="-DCONFIG_$(call qstrip,$(BR2_ENDIAN))_ENDIAN \
		-Wno-error"

$(eval $(kernel-module))
$(eval $(generic-package))
