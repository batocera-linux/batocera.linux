################################################################################
#
# openbor-common
#
################################################################################

OPENBOR_COMMON_VERSION = 1.0.0
OPENBOR_COMMON_SOURCE =
OPENBOR_COMMON_EMULATOR_INFO = openbor.emulator.yml

$(eval $(generic-package))
$(eval $(emulator-info-package))
