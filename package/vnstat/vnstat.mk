################################################################################
#
# vnstat
#
################################################################################

VNSTAT_VERSION = 2.4
VNSTAT_SITE = http://humdi.net/vnstat
VNSTAT_LICENSE = GPL-2.0
VNSTAT_LICENSE_FILES = COPYING
VNSTAT_DEPENDENCIES = host-pkgconf sqlite
VNSTAT_CONF_OPTS = --disable-extra-paths

ifeq ($(BR2_PACKAGE_GD)$(BR2_PACKAGE_LIBPNG),yy)
VNSTAT_DEPENDENCIES += gd
VNSTAT_CONF_OPTS += --enable-image-output
else
VNSTAT_CONF_OPTS += --disable-image-output
endif

$(eval $(autotools-package))
