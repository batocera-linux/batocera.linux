################################################################################
#
# rtl8821ce
#
################################################################################
# Version from July, 02 2020
RTL8821CE_VERSION = 18c1f607c10307a249be82cb398fb08eb7857a9f
RTL8821CE_SITE = https://github.com/tomaspinho/rtl8821ce.git
RTL8821CE_SITE_METHOD = git
RTL8821CE_DEPENDENCIES = linux linux-headers
RTL8821CE_INSTALL_STAGING = YES

define RTL8821CE_INSTALL_TARGET_CMDS
endef

RTL8821CE_MODULES += rtl8821ce
$(RTL8821CE_INSTALL_KERNEL_MODULE)
$(eval $(kernel-module))

$(eval $(generic-package))
