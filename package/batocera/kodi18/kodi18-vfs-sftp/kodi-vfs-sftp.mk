################################################################################
#
# kodi-vfs-sftp
#
################################################################################

KODI18_VFS_SFTP_VERSION = 1.0.5-Leia
KODI18_VFS_SFTP_SITE = $(call github,xbmc,vfs.sftp,$(KODI18_VFS_SFTP_VERSION))
KODI18_VFS_SFTP_LICENSE = GPL-2.0+
KODI18_VFS_SFTP_LICENSE_FILES = src/SFTPFile.cpp
KODI18_VFS_SFTP_DEPENDENCIES = kodi18-platform libplatform libssh

$(eval $(cmake-package))
