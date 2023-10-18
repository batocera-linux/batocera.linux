################################################################################
#
# rtl8822cs
#
################################################################################
# Version: Commits on Oct 5, 2023
RTL8822CS_VERSION = b77a5cf442fbc01c1220b8174ee2227a8f71e204
RTL8822CS_SITE = $(call github,jethome-ru,rtl88x2cs,$(RTL8822CS_VERSION))
RTL8822CS_LICENSE = GPL-2.0

RTL8822CS_MODULE_MAKE_OPTS = \
	CONFIG_RTL8822CS=m \
	KVER=$(LINUX_VERSION_PROBED) \
	KSRC=$(LINUX_DIR)

define RTL8822CS_LINUX_CONFIG_FIXUPS
    $(call KCONFIG_ENABLE_OPT,CONFIG_NET)
    $(call KCONFIG_ENABLE_OPT,CONFIG_WIRELESS)
    $(call KCONFIG_ENABLE_OPT,CONFIG_CFG80211)
    $(call KCONFIG_ENABLE_OPT,CONFIG_MAC80211)
    $(call KCONFIG_ENABLE_OPT,CONFIG_MMC)
endef

$(eval $(kernel-module))
$(eval $(generic-package))
