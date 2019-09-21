################################################################################
#
# tinyxml2
#
################################################################################

TINYXML2_VERSION = 7.0.1
TINYXML2_SITE = $(call github,leethomason,tinyxml2,$(TINYXML2_VERSION))
TINYXML2_LICENSE = Zlib
TINYXML2_LICENSE_FILES = readme.md
TINYXML2_INSTALL_STAGING = YES

ifeq ($(BR2_STATIC_LIBS),y)
TINYXML2_CONF_OPTS += -DBUILD_STATIC_LIBS=ON
endif

$(eval $(cmake-package))
