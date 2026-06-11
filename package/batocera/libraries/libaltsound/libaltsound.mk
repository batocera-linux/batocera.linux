################################################################################
#
# libaltsound
#
################################################################################
# Version: Commits on Jun 10, 2026
LIBALTSOUND_VERSION = f4b790a19ae45a9f93ae0051df6933800c7a6446
LIBALTSOUND_SITE = $(call github,vpinball,libaltsound,$(LIBALTSOUND_VERSION))
LIBALTSOUND_LICENSE = BSD-3-Clause
LIBALTSOUND_LICENSE_FILES = LICENSE
LIBALTSOUND_DEPENDENCIES = host-libcurl
LIBALTSOUND_SUPPORTS_IN_SOURCE_BUILD = NO
# Install to staging to build Visual Pinball Standalone
LIBALTSOUND_INSTALL_STAGING = YES

LIBALTSOUND_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release
LIBALTSOUND_CONF_OPTS += -DBUILD_STATIC=OFF
LIBALTSOUND_CONF_OPTS += -DPLATFORM=linux
LIBALTSOUND_CONF_OPTS += -DARCH=$(BUILD_ARCH)

# handle supported target platforms
ifeq ($(BR2_aarch64),y)
    BUILD_ARCH = aarch64
else ifeq ($(BR2_x86_64),y)
    BUILD_ARCH = x64
endif

$(eval $(cmake-package))
