################################################################################
#
# wildmidi
#
################################################################################
# Version: Commits on Mar 12, 2026
WILDMIDI_VERSION = 9ee0f9bc6db93521abd0192b226d2cf8089eb369
WILDMIDI_SITE =  $(call github,Mindwerks,wildmidi,$(WILDMIDI_VERSION))
WILDMIDI_LICENSE = LGPLv3
WILDMIDI_INSTALL_STAGING = YES

WILDMIDI_CONF_OPTS += -DBUILD_TESTING=OFF -DWANT_STATIC=ON -DWANT_PLAYER=OFF

$(eval $(cmake-package))
