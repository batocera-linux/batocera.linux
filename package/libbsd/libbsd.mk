################################################################################
#
# libbsd
#
################################################################################

LIBBSD_VERSION = 0.10.0
LIBBSD_SOURCE = libbsd-$(LIBBSD_VERSION).tar.xz
LIBBSD_SITE = https://libbsd.freedesktop.org/releases
LIBBSD_LICENSE = BSD-2-Clause, BSD-3-Clause, BSD-4-Clause, BSD-5-Clause, \
		MIT, ISC, Beerware
LIBBSD_LICENSE_FILES = COPYING
LIBBSD_INSTALL_STAGING = YES

$(eval $(autotools-package))
