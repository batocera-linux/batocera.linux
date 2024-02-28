################################################################################
#
# libjanet
#
################################################################################

LIBJANET_VERSION = v1.33.0
LIBJANET_SITE = https://github.com/janet-lang/janet.git
LIBJANET_SITE_METHOD=git
LIBJANET_LICENSE = MIT
LIBJANET_LICENSE_FILES = LICENSE
LIBJANET_INSTALL_STAGING = YES

$(eval $(meson-package))
