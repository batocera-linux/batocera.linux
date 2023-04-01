################################################################################
#
# kodi20-vfs-sftp
#
################################################################################

KODI20_VFS_SFTP_VERSION = 20.1.0-Nexus
KODI20_VFS_SFTP_SITE = $(call github,xbmc,vfs.sftp,$(KODI20_VFS_SFTP_VERSION))
KODI20_VFS_SFTP_LICENSE = GPL-2.0+
KODI20_VFS_SFTP_LICENSE_FILES = LICENSE.md
KODI20_VFS_SFTP_DEPENDENCIES = kodi20 libssh openssl zlib

$(eval $(cmake-package))
