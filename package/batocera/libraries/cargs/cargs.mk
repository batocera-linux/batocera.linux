################################################################################
#
# cargs
#
################################################################################
# Version: Commits on Apr 29, 2026
CARGS_VERSION = 0698c3f90333446d0fc2745c1e9ce10dd4a9497a
CARGS_SITE = $(call github,likle,cargs,$(CARGS_VERSION))
CARGS_LICENSE = MIT
CARGS_LICENSE_FILES = LICENSE
CARGS_DEPENDENCIES =
CARGS_SUPPORTS_IN_SOURCE_BUILD = NO

CARGS_CONF_OPTS += -DBUILD_SHARED_LIBS=On -DCMAKE_BUILD_TYPE=Release

CARGS_INSTALL_STAGING = YES

$(eval $(cmake-package))
