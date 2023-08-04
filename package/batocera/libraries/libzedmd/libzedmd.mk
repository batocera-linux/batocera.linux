################################################################################
#
# libzedmd
#
################################################################################

LIBZEDMD_VERSION = 499b1c094d49ae9bd988326475c51686b1415186
LIBZEDMD_SITE = $(call github,PPUC,libzedmd,$(LIBZEDMD_VERSION))
LIBZEDMD_LICENSE = GPLv3
LIBZEDMD_LICENSE_FILES = LICENSE
LIBZEDMD_DEPENDENCIES = 

# Install to staging to build Visual Pinball Standalone
LIBZEDMD_INSTALL_STAGING = YES

LIBZEDMD_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release

$(eval $(cmake-package))
