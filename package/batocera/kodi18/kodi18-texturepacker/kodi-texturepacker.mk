################################################################################
#
# kodi-texturepacker
#
################################################################################

# Not possible to directly refer to kodi18 variables, because of
# first/second expansion trickery...
KODI18_TEXTUREPACKER_VERSION = 18.6-Leia
KODI18_TEXTUREPACKER_SITE = $(call github,xbmc,xbmc,$(KODI18_TEXTUREPACKER_VERSION))
KODI18_TEXTUREPACKER_SOURCE = kodi18-$(KODI18_TEXTUREPACKER_VERSION).tar.gz
KODI18_TEXTUREPACKER_DL_SUBDIR = kodi18
KODI18_TEXTUREPACKER_LICENSE = GPL-2.0
KODI18_TEXTUREPACKER_LICENSE_FILES = LICENSE.md
HOST_KODI18_TEXTUREPACKER_SUBDIR = tools/depends/native/TexturePacker
HOST_KODI18_TEXTUREPACKER_DEPENDENCIES = \
	host-giflib \
	host-libjpeg \
	host-libpng \
	host-lzo

HOST_KODI18_TEXTUREPACKER_CXXFLAGS = \
	$(HOST_CXXFLAGS) \
	-std=c++0x \
	-DTARGET_POSIX \
	-DTARGET_LINUX \
	-D_LINUX \
	-I$(@D)/xbmc/linux

HOST_KODI18_TEXTUREPACKER_CONF_OPTS += \
	-DCMAKE_CXX_FLAGS="$(HOST_KODI18_TEXTUREPACKER_CXXFLAGS)" \
	-DCMAKE_MODULE_PATH=$(@D)/cmake/modules \
	-Wno-dev

define HOST_KODI18_TEXTUREPACKER_INSTALL_CMDS
	$(INSTALL) -m 755 -D \
		$(@D)/tools/depends/native/TexturePacker/TexturePacker \
		$(HOST_DIR)/bin/TexturePacker
endef

$(eval $(host-cmake-package))
