################################################################################
#
# nghttp3
#
################################################################################

NGHTTP3_VERSION = v1.12.0
NGHTTP3_SITE = https://github.com/ngtcp2/nghttp3.git
NGHTTP3_SITE_METHOD = git
NGHTTP3_GIT_SUBMODULES = YES
NGHTTP3_LICENSE = MIT license
NGHTTP3_SUPPORTS_IN_SOURCE_BUILD = NO
NGHTTP3_INSTALL_STAGING = YES
NGHTTP3_INSTALL_TARGET = NO

NGHTTP3_DEPENDENCIES = 

NGHTTP3_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release

$(eval $(cmake-package))
