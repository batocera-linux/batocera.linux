################################################################################
#
# libplacebo
#
################################################################################

LIBPLACEBO_VERSION = v7.349.0
LIBPLACEBO_SITE = https://github.com/haasn/libplacebo
LIBPLACEBO_SITE_METHOD = git
LIBPLACEBO_GIT_SUBMODULES = YES
LIBPLACEBO_LICENSE = LGPL-2.1
LIBPLACEBO_LICENSE_FILES = LICENSE
LIBPLACEBO_INSTALL_STAGING = YES

$(eval $(meson-package))
