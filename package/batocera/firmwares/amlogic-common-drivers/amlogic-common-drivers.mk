################################################################################
#
# amlogic-common-drivers
#
################################################################################

AMLOGIC_COMMON_DRIVERS_VERSION = $(call qstrip,$(BR2_PACKAGE_AMLOGIC_COMMON_DRIVERS_VERSION))
AMLOGIC_COMMON_DRIVERS_SITE = $(call qstrip,$(BR2_PACKAGE_AMLOGIC_COMMON_DRIVERS_REPOSITORY))
AMLOGIC_COMMON_DRIVERS_SITE_METHOD = git

$(eval $(generic-package))
