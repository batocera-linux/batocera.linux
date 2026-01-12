################################################################################
#
# moonlight-common
#
################################################################################

MOONLIGHT_COMMON_VERSION = 1.0.0
MOONLIGHT_COMMON_SOURCE =
MOONLIGHT_COMMON_EMULATOR_INFO = moonlight.emulator.yml

$(eval $(generic-package))
$(eval $(emulator-info-package))