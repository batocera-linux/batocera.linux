################################################################################
#
# rtl8812au
#
################################################################################
# Version: Commits on Aug 20, 2026
RTL8812AU_VERSION = 4722250273e4316daf9d8688e9916ea94c36a5ff
RTL8812AU_SITE = $(call github,morrownr,8812au-20210820,$(RTL8812AU_VERSION))
RTL8812AU_LICENSE = GPL-2.0
RTL8812AU_LICENSE_FILES = LICENSE

RTL8812AU_MODULE_MAKE_OPTS = CONFIG_RTL8812AU=m

$(eval $(kernel-module))
$(eval $(generic-package))
