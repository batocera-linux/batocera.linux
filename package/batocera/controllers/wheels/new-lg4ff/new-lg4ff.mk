################################################################################
#
# new-lg4ff
#
################################################################################
# Version: Commits on May 29, 2025
NEW_LG4FF_VERSION = 2092db19f7b40854e0427a1b2e39eda9f8d0c3cd
NEW_LG4FF_SITE = $(call github,berarma,new-lg4ff,$(NEW_LG4FF_VERSION))

$(eval $(kernel-module))
$(eval $(generic-package))
