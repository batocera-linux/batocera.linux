################################################################################
#
# rpi-utils
#
################################################################################
# Version: Commits on Jul 8, 2026
RPI_UTILS_VERSION = 5edd399260b5081f9c1c96fc7f369b920d6732d1	
RPI_UTILS_SITE = $(call github,raspberrypi,utils,$(RPI_UTILS_VERSION))
RPI_UTILS_LICENSE = BSD-3-Clause
RPI_UTILS_LICENSE_FILES = LICENCE

RPI_UTILS_DEPENDENCIES = dtc ncurses

RPI_UTILS_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release
RPI_UTILS_CONF_OPTS += -DBUILD_SHARED_LIBS=OFF

$(eval $(cmake-package))
