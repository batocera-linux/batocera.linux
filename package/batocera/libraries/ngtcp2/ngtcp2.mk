################################################################################
#
# ngtcp2
#
################################################################################

NGTCP2_VERSION = v1.16.0
NGTCP2_SITE = https://github.com/ngtcp2/ngtcp2.git
NGTCP2_SITE_METHOD = git
NGTCP2_GIT_SUBMODULES = YES
NGTCP2_LICENSE = MIT license
NGTCP2_LICENSE_FILES = COPYING

NGTCP2_INSTALL_STAGING = YES
NGTCP2_INSTALL_TARGET = NO

NGTCP2_DEPENDENCIES = libev libopenssl nghttp3

NGTCP2_CONF_OPTS = -DENABLE_OPENSSL=OFF

$(eval $(cmake-package))
