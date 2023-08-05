################################################################################
#
# kodi20-inputstream-adaptive
#
################################################################################

KODI20_INPUTSTREAM_ADAPTIVE_VERSION = 20.3.11-Nexus
KODI20_INPUTSTREAM_ADAPTIVE_SITE = $(call github,xbmc,inputstream.adaptive,$(KODI20_INPUTSTREAM_ADAPTIVE_VERSION))
KODI20_INPUTSTREAM_ADAPTIVE_LICENSE = \
	BSD-2-Clause-Views \
	BSD-3-Clause \
	google-patent-license-webm \
	GPL-2.0-or-later \
	RSA-MD5

KODI20_INPUTSTREAM_ADAPTIVE_LICENSE_FILES = \
	LICENSE.md \
	LICENSES/README.md \
	LICENSES/BSD-2-Clause-Views \
	LICENSES/BSD-3-Clause \
	LICENSES/google-patent-license-webm \
	LICENSES/GPL-2.0-or-later \
	LICENSES/RSA-MD

KODI20_INPUTSTREAM_ADAPTIVE_DEPENDENCIES = bento4 expat kodi20

$(eval $(cmake-package))