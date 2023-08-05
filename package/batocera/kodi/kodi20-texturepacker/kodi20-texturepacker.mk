################################################################################
#
# kodi20-texturepacker
#
################################################################################

# Not possible to directly refer to kodi20 variables, because of
# first/second expansion trickery...
KODI20_TEXTUREPACKER_VERSION = 20.2-Nexus
KODI20_TEXTUREPACKER_SITE = $(call github,xbmc,xbmc,$(KODI20_TEXTUREPACKER_VERSION))
KODI20_TEXTUREPACKER_SOURCE = kodi20-$(KODI20_TEXTUREPACKER_VERSION).tar.gz
KODI20_TEXTUREPACKER_DL_SUBDIR = kodi20
KODI20_TEXTUREPACKER_LICENSE = GPL-2.0
KODI20_TEXTUREPACKER_LICENSE_FILES = LICENSE.md
HOST_KODI20_TEXTUREPACKER_SUBDIR = tools/depends/native/TexturePacker
HOST_KODI20_TEXTUREPACKER_DEPENDENCIES = \
	host-giflib \
	host-libjpeg \
	host-libpng \
	host-lzo

HOST_KODI20_TEXTUREPACKER_CXXFLAGS = \
	$(HOST_CXXFLAGS) \
	-std=c++0x \
	-DTARGET_POSIX \
	-DTARGET_LINUX \
	-D_LINUX \
	-I$(@D)/xbmc/linux

HOST_KODI20_TEXTUREPACKER_CONF_OPTS += \
	-DCMAKE_CXX_FLAGS="$(HOST_KODI20_TEXTUREPACKER_CXXFLAGS)" \
	-DCMAKE_MODULE_PATH=$(@D)/cmake/modules \
	-Wno-dev

define HOST_KODI20_TEXTUREPACKER_INSTALL_CMDS
	$(INSTALL) -m 755 -D \
		$(@D)/tools/depends/native/TexturePacker/TexturePacker \
		$(HOST_DIR)/bin/TexturePacker
endef

$(eval $(host-cmake-package))
