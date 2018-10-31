################################################################################
#
# XOSD - show text over a X display
#
################################################################################

XOSD_VERSION = 2.2.14
XOSD_SOURCE = xosd-$(XOSD_VERSION).tar.gz
XOSD_SITE = https://freefr.dl.sourceforge.net/project/libxosd/libxosd/xosd-$(XOSD_VERSION)

XOSD_DEPENDENCIES = xserver_xorg-server

$(eval $(autotools-package))
