################################################################################
#
# devilutionx
#
################################################################################

DEVILUTIONX_VERSION = 1.2.1
DEVILUTIONX_SITE = $(call github,diasurgical,devilutionx,$(DEVILUTIONX_VERSION))
DEVILUTIONX_DEPENDENCIES = sdl2 sdl2_mixer sdl2_image sdl2_ttf libsodium

# Prefill the player name when creating a new character, in case the device does
# not have a keyboard.
DEVILUTIONX_CONF_OPTS += -DPREFILL_PLAYER_NAME=ON

# Define VERSION_NUM so that DevilutionX build does not attempt to get it from
# git, to which it doesn't have access here.
#
# VERSION_NUM must match (\d\.)*\d. If the DEVILUTIONX_VERSION does not
# match this pattern (tested by simply looking for a "."), we use a fixed
# version with a commit hash suffix instead.
ifeq ($(findstring .,$(DEVILUTIONX_VERSION)),.)
DEVILUTIONX_CONF_OPTS += -DVERSION_NUM=$(DEVILUTIONX_VERSION)
else
DEVILUTIONX_CONF_OPTS += -DVERSION_NUM=1.2.1 -DVERSION_SUFFIX="-$(DEVILUTIONX_VERSION)"
endif

define DEVILUTIONX_INSTALL_TARGET_CMDS
# evmap config
	mkdir -p $(TARGET_DIR)/usr/share/evmapy
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/ports/devilutionx/devilutionx.keys $(TARGET_DIR)/usr/share/evmapy
endef

$(eval $(cmake-package))
