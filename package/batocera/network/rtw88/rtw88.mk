################################################################################
#
# rtw88
#
################################################################################
# Version: Commits on May 21, 2026
RTW88_VERSION = a56bcd26e770257612a0803249cbd4095fc6feca
RTW88_SITE = $(call github,lwfinger,rtw88,$(RTW88_VERSION))

$(eval $(kernel-module))
$(eval $(generic-package))
