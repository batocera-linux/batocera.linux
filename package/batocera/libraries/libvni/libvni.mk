################################################################################
#
# libvni
#
################################################################################
# Version: Commits on Nov 6, 2026
LIBVNI_VERSION = c878f7dbfd9e9cec33bcbf0e896f1188a01933b8
LIBVNI_SITE = $(call github,PPUC,libvni,$(LIBVNI_VERSION))
LIBVNI_LICENSE = GPLv2
LIBVNI_LICENSE_FILES = LICENSE.md
LIBVNI_DEPENDENCIES = libframeutil
LIBVNI_SUPPORTS_IN_SOURCE_BUILD = NO
LIBVNI_INSTALL_STAGING = YES

LIBVNI_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release
LIBVNI_CONF_OPTS += -DBUILD_STATIC=OFF
LIBVNI_CONF_OPTS += -DPLATFORM=linux
LIBVNI_CONF_OPTS += -DARCH=$(BUILD_ARCH)

ifeq ($(BR2_aarch64),y)
    BUILD_ARCH = aarch64
else ifeq ($(BR2_x86_64),y)
    BUILD_ARCH = x64
endif

$(eval $(cmake-package))
