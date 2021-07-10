################################################################################
#
# pulsemixer
#
################################################################################
PULSEMIXER_VERSION = 1.5.1
PULSEMIXER_SITE = $(call github,GeorgeFilipkin,pulsemixer,$(PULSEMIXER_VERSION))
PULSEMIXER_LICENSE = MIT
PULSEMIXER_LICENSE_FILES = LICENSE
PULSEMIXER_SETUP_TYPE = distutils
PULSEMIXER_DEPENDENCIES = python3 pulseaudio-utils

$(eval $(python-package))
