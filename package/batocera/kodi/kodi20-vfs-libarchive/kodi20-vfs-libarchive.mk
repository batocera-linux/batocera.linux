################################################################################
#
# kodi20-vfs-libarchive
#
################################################################################

KODI20_VFS_LIBARCHIVE_VERSION = 20.1.0-Nexus
KODI20_VFS_LIBARCHIVE_SITE = $(call github,xbmc,vfs.libarchive,$(KODI20_VFS_LIBARCHIVE_VERSION))
KODI20_VFS_LIBARCHIVE_LICENSE = GPL-2.0+
KODI20_VFS_LIBARCHIVE_LICENSE_FILES = LICENSE.md
KODI20_VFS_LIBARCHIVE_DEPENDENCIES = \
	bzip2 \
	kodi20 \
	libarchive \
	lz4 \
	lzo \
	openssl \
	xz \
	zlib

$(eval $(cmake-package))
