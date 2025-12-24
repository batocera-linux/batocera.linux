################################################################################
#
# rpi-utils
#
################################################################################
# Version: Commits on Dec 18, 2025
RPI_UTILS_VERSION = 230d67ad28e74b17a42064453b2163991cb51a5e
RPI_UTILS_SITE = $(call github,raspberrypi,utils,$(RPI_UTILS_VERSION))
RPI_UTILS_LICENSE = BSD-3-Clause
RPI_UTILS_LICENSE_FILES = LICENCE

RPI_UTILS_DEPENDENCIES = dtc

RPI_UTILS_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release
RPI_UTILS_CONF_OPTS += -DBUILD_SHARED_LIBS=OFF

$(eval $(cmake-package))
