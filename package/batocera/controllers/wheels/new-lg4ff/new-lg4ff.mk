################################################################################
#
# new-lg4ff
#
################################################################################
# Version: Commits on Dec 27, 2024
NEW_LG4FF_VERSION = e5ca8d620c077d5829d24b0efa4ee0e52148d499
NEW_LG4FF_SITE = $(call github,berarma,new-lg4ff,$(NEW_LG4FF_VERSION))

$(eval $(kernel-module))
$(eval $(generic-package))
