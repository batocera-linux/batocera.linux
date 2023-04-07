################################################################################
#
# kodi20-inputstream-rtmp
#
################################################################################

KODI20_INPUTSTREAM_RTMP_VERSION = 20.3.0-Nexus
KODI20_INPUTSTREAM_RTMP_SITE = $(call github,xbmc,inputstream.rtmp,$(KODI20_INPUTSTREAM_RTMP_VERSION))
KODI20_INPUTSTREAM_RTMP_LICENSE = GPL-2.0+
KODI20_INPUTSTREAM_RTMP_LICENSE_FILES = LICENSE.md
KODI20_INPUTSTREAM_RTMP_DEPENDENCIES = kodi20 openssl rtmpdump zlib

$(eval $(cmake-package))
