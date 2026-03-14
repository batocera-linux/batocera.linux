################################################################################
#
# cemu-common
#
################################################################################

CEMU_COMMON_VERSION = 1.0.0
CEMU_COMMON_SOURCE =
CEMU_COMMON_EMULATOR_INFO = cemu.emulator.yml

$(eval $(generic-package))
$(eval $(emulator-info-package))
