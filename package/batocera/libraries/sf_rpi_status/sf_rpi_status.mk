################################################################################
#
# sf_rpi_status
#
################################################################################
# Version: Commits on Jan 16, 2025
SF_RPI_STATUS_VERSION = 7f7fa9d42f2d62a6b5faf9efc6a01577fc2c38c1
SF_RPI_STATUS_SITE = $(call github,sunfounder,sf_rpi_status,$(SF_RPI_STATUS_VERSION))
SF_RPI_STATUS_SETUP_TYPE = setuptools
SF_RPI_STATUS_LICENSE = GPL-2.0
SF_RPI_STATUS_LICENSE_FILES = LICENSE

SF_RPI_STATUS_DEPENDENCIES = python-requests python-psutil

$(eval $(python-package))
