################################################################################
#
# duckstation-common
#
################################################################################

DUCKSTATION_COMMON_VERSION = 1.0.0
DUCKSTATION_COMMON_SOURCE =
$(eval $(call register,duckstation.emulator.yml))
$(eval $(call register-if-kconfig,BR2_PACKAGE_BATOCERA_VULKAN,gfxbackend.duckstation.emulator.yml))

$(eval $(generic-package))
$(eval $(emulator-info-package))
