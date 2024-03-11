################################################################################
#
# sockpp
#
################################################################################
# Version: Commits on Mar 11, 2024
SOCKPP_VERSION = e6c4688a576d95f42dd7628cefe68092f6c5cd0f
SOCKPP_SITE = $(call github,fpagliughi,sockpp,$(SOCKPP_VERSION))
SOCKPP_LICENSE = BSD-3-Clause
SOCKPP_LICENSE_FILES = LICENSE
SOCKPP_DEPENDENCIES =
SOCKPP_SUPPORTS_IN_SOURCE_BUILD = NO

SOCKPP_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release

SOCKPP_INSTALL_STAGING = YES

$(eval $(cmake-package))
