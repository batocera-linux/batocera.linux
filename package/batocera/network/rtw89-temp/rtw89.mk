################################################################################
#
# rtw89-temp
#
################################################################################
# Version: Commits on Jan 18, 2023
RTW89_TEMP_VERSION = fce040c12fbf93bfd904ded48df60dea2c8d4423
RTW89_TEMP_SITE = $(call github,lwfinger,rtw89,$(RTW89_TEMP_VERSION))
RTW89_TEMP_LICENSE = GPL-2.0
RTW89_TEMP_LICENSE_FILES = LICENSE

RTW89_TEMP_MODULE_MAKE_OPTS = \
	CONFIG_RTW89_TEMP=m \
	USER_EXTRA_CFLAGS="-DCONFIG_$(call qstrip,$(BR2_ENDIAN))_ENDIAN \
		-Wno-error"

define RTW89_TEMP_MAKE_SUBDIR
        (cd $(@D); ln -s . RTW89)
endef

RTW89_TEMP_PRE_CONFIGURE_HOOKS += RTW89_TEMP_MAKE_SUBDIR

$(eval $(kernel-module))
$(eval $(generic-package))
