################################################################################
#
# LIBXMP
#
################################################################################

LIBXMP_VERSION = 4.7.2
LIBXMP_SOURCE = enet-libxmp-${LIBXMP_VERSION}.tar.gz
LIBXMP_SITE =  $(call github,libxmp,libxmp,$(LIBXMP_VERSION))
LIBXMP_INSTALL_STAGING = YES
LIBXMP_AUTORECONF = YES
LIBXMP_DEPENDENCIES = host-pkgconf

$(eval $(autotools-package))
