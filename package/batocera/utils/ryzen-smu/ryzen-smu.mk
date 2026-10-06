################################################################################
#
# ryzen-smu
#
################################################################################
# Version: Commits on Aug 15, 2026
RYZEN_SMU_VERSION = d2983668300dd2a598e5a7dc40e71ce0678cc270
RYZEN_SMU_SITE = $(call github,amkillam,ryzen_smu,$(RYZEN_SMU_VERSION))
RYZEN_SMU_LICENSE = GPL-2.0
RYZEN_SMU_LICENSE_FILES = LICENSE

RYZEN_SMU_MODULE_MAKE_OPTS = \
    USER_EXTRA_CFLAGS="-DCONFIG_$(call qstrip,$(BR2_ENDIAN))_ENDIAN -Wno-error"

$(eval $(kernel-module))
$(eval $(generic-package))
