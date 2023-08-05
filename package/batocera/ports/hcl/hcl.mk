################################################################################
#
# Hydra Castle Labyrinth
#
################################################################################
# Version.: Commits on Jun 24, 2022
HCL_VERSION = a4000681a20cd6639183cf72a722f4c2daf30cc7
HCL_SITE = $(call github,ptitSeb,hydracastlelabyrinth,$(HCL_VERSION))

HCL_DEPENDENCIES = sdl2 sdl2_mixer
HCL_LICENSE = GPL-2.0

HCL_SUPPORTS_IN_SOURCE_BUILD = NO

HCL_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release -DUSE_SDL2=ON

define HCL_INSTALL_TARGET_CMDS
	cp $(@D)/buildroot-build/hcl $(TARGET_DIR)/usr/bin/hcl
	chmod 0754 $(TARGET_DIR)/usr/bin/hcl
	# evmap config
	mkdir -p $(TARGET_DIR)/usr/share/evmapy
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/ports/hcl/hcl.keys $(TARGET_DIR)/usr/share/evmapy
endef

$(eval $(cmake-package))
