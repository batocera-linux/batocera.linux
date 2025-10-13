################################################################################
#
# cxxopts
#
################################################################################

CXXOPTS_VERSION = v3.3.1
CXXOPTS_SITE = $(call github,jarro2783,cxxopts,$(CXXOPTS_VERSION))
CXXOPTS_LICENSE = MIT license
CXXOPTS_LICENSE_FILES = LICENSE
CXXOPTS_SUPPORTS_IN_SOURCE_BUILD = NO
CXXOPTS_INSTALL_STAGING = YES
CXXOPTS_INSTALL_TARGET = NO

CXXOPTS_DEPENDENCIES = 

CXXOPTS_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release

$(eval $(cmake-package))
