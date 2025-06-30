################################################################################
#
# ryzen-smu
#
################################################################################
# Version: Commits on Jun 4, 2025
RYZEN_SMU_VERSION = 9f9569f889935f7c7294cc32c1467e5a4081701a
RYZEN_SMU_SITE = $(call github,amkillam,ryzen_smu,$(RYZEN_SMU_VERSION))
RYZEN_SMU_LICENSE = GPL-2.0
RYZEN_SMU_LICENSE_FILES = LICENSE

RYZEN_SMU_MODULE_MAKE_OPTS = \
    USER_EXTRA_CFLAGS="-DCONFIG_$(call qstrip,$(BR2_ENDIAN))_ENDIAN -Wno-error"

$(eval $(kernel-module))
$(eval $(generic-package))
