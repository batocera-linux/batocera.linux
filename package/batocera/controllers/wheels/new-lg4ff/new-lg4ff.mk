################################################################################
#
# new-lg4ff
#
################################################################################
# Version: Commits on Dec 30, 2023
NEW_LG4FF_VERSION = 89d2b09bc762d62581a385a7d11533ccc1eb3319
NEW_LG4FF_SITE = $(call github,berarma,new-lg4ff,$(NEW_LG4FF_VERSION))

$(eval $(kernel-module))
$(eval $(generic-package))
