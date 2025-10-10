################################################################################
#
# ryzen-smu
#
################################################################################
# Version: Commits on Aug 10, 2025
RYZEN_SMU_VERSION = 172c316f53ac8f066afd7cb9e1da517084273368
RYZEN_SMU_SITE = $(call github,amkillam,ryzen_smu,$(RYZEN_SMU_VERSION))
RYZEN_SMU_LICENSE = GPL-2.0
RYZEN_SMU_LICENSE_FILES = LICENSE

RYZEN_SMU_MODULE_MAKE_OPTS = \
    USER_EXTRA_CFLAGS="-DCONFIG_$(call qstrip,$(BR2_ENDIAN))_ENDIAN -Wno-error"

$(eval $(kernel-module))
$(eval $(generic-package))
