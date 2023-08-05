################################################################################
#
# rtl8821au-morrownr
#
################################################################################

RTL8821AU_MORROWNR_VERSION = 19660ee3f67125d2ef31b626f9fff946bd3e8d01
RTL8821AU_MORROWNR_SITE = $(call github,morrownr,8821au-20210708,$(RTL8821AU_MORROWNR_VERSION))
RTL8821AU_MORROWNR_LICENSE = GPL-2.0
RTL8821AU_MORROWNR_LICENSE_FILES = LICENSE

RTL8821AU_MORROWNR_MODULE_MAKE_OPTS = \
	CONFIG_RTL8821AU=m \
	USER_EXTRA_CFLAGS="-DCONFIG_$(call qstrip,$(BR2_ENDIAN))_ENDIAN \
		-Wno-error"

define RTL8821AU_MORROWNR_MAKE_SUBDIR
        (cd $(@D); ln -s . RTL8821AU)
endef

RTL8821AU_MORROWNR_PRE_CONFIGURE_HOOKS += RTL8821AU_MORROWNR_MAKE_SUBDIR

$(eval $(kernel-module))
$(eval $(generic-package))
