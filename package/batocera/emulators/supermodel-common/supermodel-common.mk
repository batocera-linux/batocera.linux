################################################################################
#
# supermodel-common
#
################################################################################

SUPERMODEL_COMMON_VERSION = 1.0.0
SUPERMODEL_COMMON_SOURCE =
SUPERMODEL_COMMON_EMULATOR_INFO = supermodel.emulator.yml

$(eval $(generic-package))
$(eval $(emulator-info-package))
