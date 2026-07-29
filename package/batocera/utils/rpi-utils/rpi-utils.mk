################################################################################
#
# rpi-utils
#
################################################################################
# Version: Commits on Jul 25, 2026
RPI_UTILS_VERSION = 292dbe7e35296e556d839a0b9ae2ca957ac8c961	
RPI_UTILS_SITE = $(call github,raspberrypi,utils,$(RPI_UTILS_VERSION))
RPI_UTILS_LICENSE = BSD-3-Clause
RPI_UTILS_LICENSE_FILES = LICENCE

RPI_UTILS_DEPENDENCIES = dtc ncurses

RPI_UTILS_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release
RPI_UTILS_CONF_OPTS += -DBUILD_SHARED_LIBS=OFF

$(eval $(cmake-package))
