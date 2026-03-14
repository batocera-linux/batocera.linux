################################################################################
#
# wine-common
#
################################################################################

WINE_COMMON_VERSION = 1.0.0
WINE_COMMON_SOURCE =
WINE_COMMON_EMULATOR_INFO = wine.emulator.yml mugen.emulator.yml

$(eval $(generic-package))
$(eval $(emulator-info-package))

