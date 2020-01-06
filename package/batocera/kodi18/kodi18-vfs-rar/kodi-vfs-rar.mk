################################################################################
#
# kodi-vfs-rar
#
################################################################################

KODI18_VFS_RAR_VERSION = 60f92ff28ee6c94211b628990696c60518bffcf6
KODI18_VFS_RAR_SITE = $(call github,xbmc,vfs.rar,$(KODI18_VFS_RAR_VERSION))
KODI18_VFS_RAR_LICENSE = unrar, GPL-2.0+
KODI18_VFS_RAR_LICENSE_FILES = lib/UnrarXLib/license.txt src/RarManager.h
KODI18_VFS_RAR_DEPENDENCIES = libplatform kodi18

$(eval $(cmake-package))
