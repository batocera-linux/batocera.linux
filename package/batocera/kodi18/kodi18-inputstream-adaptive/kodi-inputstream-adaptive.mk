################################################################################
#
# kodi-inputstream-adaptive
#
################################################################################

KODI18_INPUTSTREAM_ADAPTIVE_VERSION = 2.4.2-Leia
KODI18_INPUTSTREAM_ADAPTIVE_SITE = $(call github,peak3d,inputstream.adaptive,$(KODI18_INPUTSTREAM_ADAPTIVE_VERSION))
KODI18_INPUTSTREAM_ADAPTIVE_LICENSE = GPL-2.0+
KODI18_INPUTSTREAM_ADAPTIVE_LICENSE_FILES = src/main.cpp
KODI18_INPUTSTREAM_ADAPTIVE_DEPENDENCIES = kodi18

$(eval $(cmake-package))
