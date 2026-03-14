################################################################################
#
# semver
#
################################################################################

SEMVER_VERSION = v1.0.0-rc
SEMVER_SITE = $(call github,Neargye,semver,$(SEMVER_VERSION))
SEMVER_LICENSE = MIT license
SEMVER_LICENSE_FILES = LICENSE
SEMVER_SUPPORTS_IN_SOURCE_BUILD = NO
SEMVER_INSTALL_STAGING = YES
SEMVER_INSTALL_TARGET = NO

SEMVER_DEPENDENCIES = 

SEMVER_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release

$(eval $(cmake-package))
