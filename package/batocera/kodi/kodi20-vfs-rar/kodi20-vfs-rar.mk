################################################################################
#
# kodi20-vfs-rar
#
################################################################################

KODI20_VFS_RAR_VERSION = 20.1.0-Nexus
KODI20_VFS_RAR_SITE = $(call github,xbmc,vfs.rar,$(KODI20_VFS_RAR_VERSION))
KODI20_VFS_RAR_LICENSE = unrar, GPL-2.0+
KODI20_VFS_RAR_LICENSE_FILES = lib/UnrarXLib/license.txt LICENSE.md
KODI20_VFS_RAR_DEPENDENCIES = kodi20 tinyxml

$(eval $(cmake-package))
