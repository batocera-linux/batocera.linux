################################################################################
#
# tomlplusplus
#
################################################################################

TOMLPLUSPLUS_VERSION = e7aaccca3fa3dbde9818ab8313250f3da4976e37
TOMLPLUSPLUS_SITE = $(call github,marzer,tomlplusplus,$(TOMLPLUSPLUS_VERSION))
TOMLPLUSPLUS_LICENSE = MIT license
TOMLPLUSPLUS_LICENSE_FILES = LICENSE
TOMLPLUSPLUS_SUPPORTS_IN_SOURCE_BUILD = NO
TOMLPLUSPLUS_INSTALL_STAGING = YES
TOMLPLUSPLUS_INSTALL_TARGET = NO

TOMLPLUSPLUS_DEPENDENCIES = 

TOMLPLUSPLUS_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release

$(eval $(cmake-package))
