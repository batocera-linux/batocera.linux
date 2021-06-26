################################################################################
#
# rtl8723ds
#
################################################################################

RTL8723DS_VERSION = f3167881f4668da0fb7f3d5c90746ff64e1c6633
RTL8723DS_SITE = $(call github,lwfinger,rtl8723ds,$(RTL8723DS_VERSION))
RTL8723DS_LICENSE = GPL-2.0
RTL8723DS_LICENSE_FILES = LICENSE

RTL8723DS_MODULE_MAKE_OPTS = \
	CONFIG_RTL8723DS=m \
# batocera: setting KVER breaks top level parallelization
	# KVER=$(LINUX_VERSION_PROBED)
	USER_EXTRA_CFLAGS="-DCONFIG_$(call qstrip,$(BR2_ENDIAN))_ENDIAN \
		-Wno-error"

$(eval $(kernel-module))
$(eval $(generic-package))
