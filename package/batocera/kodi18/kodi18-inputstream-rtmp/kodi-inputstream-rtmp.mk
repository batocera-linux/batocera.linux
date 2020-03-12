################################################################################
#
# kodi-inputstream-rtmp
#
################################################################################

KODI18_INPUTSTREAM_RTMP_VERSION = 2.0.9-Leia
KODI18_INPUTSTREAM_RTMP_SITE = $(call github,xbmc,inputstream.rtmp,$(KODI18_INPUTSTREAM_RTMP_VERSION))
KODI18_INPUTSTREAM_RTMP_LICENSE = GPL-2.0+
KODI18_INPUTSTREAM_RTMP_LICENSE_FILES = debian/copyright
KODI18_INPUTSTREAM_RTMP_DEPENDENCIES = kodi18 rtmpdump

$(eval $(cmake-package))
