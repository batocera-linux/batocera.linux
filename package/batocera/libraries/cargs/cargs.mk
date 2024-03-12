################################################################################
#
# cargs
#
################################################################################
# Version: Commits on Mar 11, 2024
CARGS_VERSION = 82b51a3fd781ba978ab9bb6a05306ce777ecb2a1
CARGS_SITE = $(call github,likle,cargs,$(CARGS_VERSION))
CARGS_LICENSE = MIT
CARGS_LICENSE_FILES = LICENSE
CARGS_DEPENDENCIES =
CARGS_SUPPORTS_IN_SOURCE_BUILD = NO

CARGS_CONF_OPTS += -DBUILD_SHARED_LIBS=On -DCMAKE_BUILD_TYPE=Release

CARGS_INSTALL_STAGING = YES

$(eval $(cmake-package))
