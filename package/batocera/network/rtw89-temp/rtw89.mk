################################################################################
#
# rtw89-temp
#
################################################################################
# Version: Commits on Dec 1, 2025
RTW89_TEMP_VERSION = e47a21c53cbd3bb4d29a42c40ca0c0c2aa005d1b
RTW89_TEMP_SITE = $(call github,morrownr,rtw89,$(RTW89_TEMP_VERSION))
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
