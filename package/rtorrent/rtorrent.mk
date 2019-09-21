################################################################################
#
# rtorrent
#
################################################################################

RTORRENT_VERSION = 0.9.8
RTORRENT_SITE = http://rtorrent.net/downloads
RTORRENT_DEPENDENCIES = host-pkgconf libcurl libtorrent ncurses
RTORRENT_LICENSE = GPL-2.0
RTORRENT_LICENSE_FILES = COPYING

$(eval $(autotools-package))
