################################################################################
#
# WildMIDI
#
################################################################################
# Version.: Commits on Nov 25, 2020
WILDMIDI_VERSION = cf91b2ce92f715cbd06d72d394a6d8837df2ea1a
WILDMIDI_SITE =  $(call github,Mindwerks,wildmidi,$(WILDMIDI_VERSION))
WILDMIDI_LICENSE = LGPLv3
WILDMIDI_INSTALL_STAGING = YES

WILDMIDI_CONF_OPTS += -DBUILD_TESTING=OFF -DWANT_STATIC=ON -DWANT_PLAYER=OFF 

$(eval $(cmake-package))
