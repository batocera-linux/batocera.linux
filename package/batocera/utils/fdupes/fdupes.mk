################################################################################
#
# fdupes
#
################################################################################
FDUPES_VERSION = 791fc12a093b77e8e897241bff731d6ec1e8f5b9
FDUPES_SITE = $(call github,adrianlopezroche,fdupes,$(FDUPES_VERSION))
FDUPES_AUTORECONF = YES
# fdupes needs curses.h but full ncurses support is disabled
FDUPES_DEPENDENCIES = ncurses
FDUPES_CONF_OPTS = --without-ncurses

$(eval $(autotools-package))
