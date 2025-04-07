################################################################################
#
# rpi-utils
#
################################################################################
# Version: Commits on Mar 18, 2025
RPI_UTILS_VERSION = 92900c5c733c8b91a67b1772d4f0a25104f2b05d
RPI_UTILS_SITE = $(call github,raspberrypi,utils,$(RPI_UTILS_VERSION))
RPI_UTILS_LICENSE = BSD-3-Clause
RPI_UTILS_LICENSE_FILES = LICENCE

RPI_UTILS_DEPENDENCIES = dtc

RPI_UTILS_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release
RPI_UTILS_CONF_OPTS += -DBUILD_SHARED_LIBS=OFF

$(eval $(cmake-package))
