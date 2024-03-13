################################################################################
#
# libportmidi
#
################################################################################

LIBPORTMIDI_VERSION = v2.0.4
LIBPORTMIDI_SITE = $(call github,PortMidi,portmidi,$(LIBPORTMIDI_VERSION))
LIBPORTMIDI_LICENSE = PortMidi
LIBPORTMIDI_LICENSE_FILES = license.txt
LIBPORTMIDI_DEPENDENCIES = alsa-lib

LIBPORTMIDI_INSTALL_STAGING = YES
LIBPORTMIDI_SUPPORTS_IN_SOURCE_BUILD = NO

LIBPORTMIDI_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release

$(eval $(cmake-package))

