################################################################################
#
# rpi-utils
#
################################################################################

RPI_UTILS_VERSION = a1d522f0f1b50858a44fac80523a2bd80098e789
RPI_UTILS_SITE = $(call github,raspberrypi,utils,$(RPI_UTILS_VERSION))
RPI_UTILS_LICENSE = BSD-3-Clause
RPI_UTILS_LICENSE_FILES = LICENCE

RPI_UTILS_DEPENCIES = dtc

$(eval $(cmake-package))
