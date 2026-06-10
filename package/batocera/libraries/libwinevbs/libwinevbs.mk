################################################################################
#
# libwinevbs
#
################################################################################
# Version: Commits on Jun 2, 2026
LIBWINEVBS_VERSION = ff26b571d4060aaafb9e093d81a749b0897013ca
LIBWINEVBS_SITE = $(call github,vpinball,libwinevbs,$(LIBWINEVBS_VERSION))
LIBWINEVBS_LICENSE = LGPL-2.1
LIBWINEVBS_LICENSE_FILES = LICENSE
LIBWINEVBS_DEPENDENCIES =
LIBWINEVBS_SUPPORTS_IN_SOURCE_BUILD = NO
LIBWINEVBS_INSTALL_STAGING = YES

LIBWINEVBS_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release
LIBWINEVBS_CONF_OPTS += -DBUILD_STATIC=OFF
LIBWINEVBS_CONF_OPTS += -DPLATFORM=linux
LIBWINEVBS_CONF_OPTS += -DARCH=$(BUILD_ARCH)

ifeq ($(BR2_aarch64),y)
    BUILD_ARCH = aarch64
else ifeq ($(BR2_x86_64),y)
    BUILD_ARCH = x64
endif

$(eval $(cmake-package))
