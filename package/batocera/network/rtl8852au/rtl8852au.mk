################################################################################
#
# rtl8852au
#
################################################################################
# Version: Commits on May 7, 2024
RTL8852AU_VERSION = 865ab0fa91471d595c283d2f3db323f7f15455f5
RTL8852AU_SITE = $(call github,lwfinger,rtl8852au,$(RTL8852AU_VERSION))
RTL8852AU_LICENSE = GPL-2.0
RTL8852AU_LICENSE_FILES = LICENSE

RTL8852AU_MODULE_MAKE_OPTS = \
	CONFIG_RTL8852AU=m \
	KVER=$(LINUX_VERSION_PROBED)
	USER_EXTRA_CFLAGS="-DCONFIG_$(call qstrip,$(BR2_ENDIAN))_ENDIAN \
		-Wno-error"

$(eval $(kernel-module))
$(eval $(generic-package))
