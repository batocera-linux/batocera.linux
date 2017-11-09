################################################################################
#
# OPENAL-SOFT
#
################################################################################

OPENAL_SOFT_VERSION = openal-soft-1.18.2
OPENAL_SOFT_SITE = $(call github,kcat,openal-soft,$(OPENAL_SOFT_VERSION))
OPENAL_SOFT_INSTALL_STAGING = YES

$(eval $(cmake-package))
