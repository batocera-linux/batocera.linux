################################################################################
#
# hcl (Hydra Castle Labyrinth)
#
################################################################################
# Version: Commits on Aug 11, 2026
HCL_VERSION = e31648688434a789e3056e52cdf1b9a842eeed48
HCL_SITE = $(call github,ptitSeb,hydracastlelabyrinth,$(HCL_VERSION))

HCL_DEPENDENCIES = sdl2 sdl2_mixer
HCL_LICENSE = GPL-2.0
HCL_EMULATOR_INFO = hcl.emulator.yml

HCL_SUPPORTS_IN_SOURCE_BUILD = NO

HCL_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release
HCL_CONF_OPTS += -DUSE_SDL2=ON
HCL_CONF_OPTS += -DCMAKE_POLICY_VERSION_MINIMUM=3.5

define HCL_INSTALL_TARGET_CMDS
	cp $(@D)/buildroot-build/hcl $(TARGET_DIR)/usr/bin/hcl
	chmod 0754 $(TARGET_DIR)/usr/bin/hcl
endef

$(eval $(cmake-package))
$(eval $(emulator-info-package))
