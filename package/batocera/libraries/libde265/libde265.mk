################################################################################
#
# libde265
#
################################################################################


LIBDE265_VERSION = v1.0.8
LIBDE265_SITE =  $(call github,strukturag,libde265,$(LIBDE265_VERSION))
LIBDE265_LICENSE = LGPLv3
LIBDE265_INSTALL_STAGING = YES

$(eval $(cmake-package))
