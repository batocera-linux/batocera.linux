################################################################################
#
# fdupes
#
################################################################################

FDUPES_VERSION = 791fc12a093b77e8e897241bff731d6ec1e8f5b9
FDUPES_SITE = $(call github,adrianlopezroche,fdupes,$(FDUPES_VERSION))

FDUPES_DEPENDENCIES = host-autoconf host-automake host-libtool
FDUPES_CONF_OPTS = --without-ncurses

define FDUPES_RUN_AUTOCONF
        (cd $(@D); $(HOST_DIR)/bin/autoreconf --install)
endef

FDUPES_PRE_CONFIGURE_HOOKS += FDUPES_RUN_AUTOCONF

$(eval $(autotools-package))
