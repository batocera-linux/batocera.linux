################################################################################
#
# xwiimote
#
################################################################################

XWIIMOTE_VERSION = f2be57e24fc24652308840cec2ed702b9d1138df
XWIIMOTE_SITE = $(call github,dvdhrm,xwiimote,$(XWIIMOTE_VERSION))

XWIIMOTE_DEPENDENCIES = udev ncurses
XWIIMOTE_AUTORECONF = YES

$(eval $(autotools-package))
