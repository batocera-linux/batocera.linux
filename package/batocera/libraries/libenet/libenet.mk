################################################################################
#
# libenet
#
################################################################################

LIBENET_VERSION = 1.3.17
LIBENET_SOURCE = enet-${LIBENET_VERSION}.tar.gz
LIBENET_SITE = http://enet.bespin.org/download
LIBENET_INSTALL_STAGING = YES
LIBENET_AUTORECONF = YES
LIBENET_DEPENDENCIES = host-pkgconf

$(eval $(autotools-package))
