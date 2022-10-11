################################################################################
#
# fdupes
#
################################################################################
FDUPES_VERSION = v2.2.1
FDUPES_SITE = $(call github,adrianlopezroche,fdupes,$(FDUPES_VERSION))
FDUPES_AUTORECONF = YES
# fdupes needs curses.h but full ncurses support is disabled
FDUPES_DEPENDENCIES = ncurses
FDUPES_CONF_OPTS = --without-ncurses

$(eval $(autotools-package))
