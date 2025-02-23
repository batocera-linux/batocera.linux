################################################################################
#
# pm_dashboard
#
################################################################################
# Version: Commits on Feb 21, 2025
PM_DASHBOARD_VERSION = fab6bed940db1cd30218081c308cf044624d330d
PM_DASHBOARD_SITE = $(call github,sunfounder,pm_dashboard,$(PM_DASHBOARD_VERSION))
PM_DASHBOARD_SETUP_TYPE = setuptools
PM_DASHBOARD_LICENSE = GPL-2.0
PM_DASHBOARD_LICENSE_FILES = LICENSE

PM_DASHBOARD_DEPENDENCIES = python-influxdb python-flask python-flask-cors influxdb

$(eval $(python-package))
