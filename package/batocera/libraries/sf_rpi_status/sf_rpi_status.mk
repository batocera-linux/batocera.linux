################################################################################
#
# sf_rpi_status
#
################################################################################
# Version: Commits on Jul 4, 2024
SF_RPI_STATUS_VERSION = 09b3e252308328b932d678d04d4d7c87798d2748
SF_RPI_STATUS_SITE = $(call github,sunfounder,sf_rpi_status,$(SF_RPI_STATUS_VERSION))
SF_RPI_STATUS_SETUP_TYPE = setuptools
SF_RPI_STATUS_LICENSE = GPL-2.0
SF_RPI_STATUS_LICENSE_FILES = LICENSE

SF_RPI_STATUS_DEPENDENCIES = python-requests python-psutil

$(eval $(python-package))
