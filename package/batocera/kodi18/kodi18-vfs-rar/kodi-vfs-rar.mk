################################################################################
#
# kodi-vfs-rar
#
################################################################################

KODI18_VFS_RAR_VERSION = 2.3.1-Leia
KODI18_VFS_RAR_SITE = $(call github,xbmc,vfs.rar,$(KODI18_VFS_RAR_VERSION))
KODI18_VFS_RAR_LICENSE = unrar, GPL-2.0+
KODI18_VFS_RAR_LICENSE_FILES = lib/UnrarXLib/license.txt LICENSE.md
KODI18_VFS_RAR_DEPENDENCIES = kodi18 tinyxml

$(eval $(cmake-package))
