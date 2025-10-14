################################################################################
#
# rpi-utils
#
################################################################################
# Version: Commits on Oct 3, 2025
RPI_UTILS_VERSION = 9f61b87db715fe9729305e242de8412d8db4153c
RPI_UTILS_SITE = $(call github,raspberrypi,utils,$(RPI_UTILS_VERSION))
RPI_UTILS_LICENSE = BSD-3-Clause
RPI_UTILS_LICENSE_FILES = LICENCE

RPI_UTILS_DEPENDENCIES = dtc

RPI_UTILS_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release
RPI_UTILS_CONF_OPTS += -DBUILD_SHARED_LIBS=OFF

$(eval $(cmake-package))
