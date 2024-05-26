################################################################################
#
# WildMIDI
#
################################################################################
# Version.: Release on Jan 14, 2023
WILDMIDI_VERSION = wildmidi-0.4.5
WILDMIDI_SITE =  $(call github,Mindwerks,wildmidi,$(WILDMIDI_VERSION))
WILDMIDI_LICENSE = LGPLv3
WILDMIDI_INSTALL_STAGING = YES

WILDMIDI_CONF_OPTS += -DBUILD_TESTING=OFF -DWANT_STATIC=ON -DWANT_PLAYER=OFF

$(eval $(cmake-package))
