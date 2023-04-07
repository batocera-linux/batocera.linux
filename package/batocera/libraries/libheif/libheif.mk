################################################################################
#
# libheif
#
################################################################################


LIBHEIF_VERSION = v1.12.0
LIBHEIF_SITE =  $(call github,strukturag,libheif,$(LIBHEIF_VERSION))
LIBHEIF_LICENSE = LGPLv3
LIBHEIF_INSTALL_STAGING = YES
LIBHEIF_DEPENDENCIES = libde265

LIBHEIF_CONF_OPTS = -DBUILD_SHARED_LIBS=0 -DLIBHEIF_STATIC_BUILD=1 -DWITH_EXAMPLES=0 -DWITH_X265=0 -DWITH_RAV1E=0 -DWITH_AOM=0 -DWITH_DAV1D=0

$(eval $(cmake-package))
