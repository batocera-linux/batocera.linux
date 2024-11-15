################################################################################
#
# devilutionx
#
################################################################################

DEVILUTIONX_VERSION = 1.5.3
DEVILUTIONX_SITE = \
    https://github.com/diasurgical/devilutionX/releases/download/$(DEVILUTIONX_VERSION)
DEVILUTIONX_SOURCE = devilutionx-src.tar.xz
DEVILUTIONX_DEPENDENCIES = sdl2 sdl2_image fmt libsodium libpng bzip2
DEVILUTIONX_SUPPORTS_IN_SOURCE_BUILD = NO

DEVILUTIONX_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release
DEVILUTIONX_CONF_OPTS += -DBUILD_TESTING=OFF
# Prefill the player name when creating a new character,
# in case the device does not have a keyboard.
DEVILUTIONX_CONF_OPTS += -DPREFILL_PLAYER_NAME=ON                         
# Ensure that DevilutionX's vendored dependencies are not accidentally fetched from network.
# They should all be present in the source package.
DEVILUTIONX_CONF_OPTS += -DFETCHCONTENT_FULLY_DISCONNECTED=ON

# ZeroTier on aarch64 uses ARMv8 Cryptography Extensions.
# These extension are optional and only certain Armv8-A CPUs support them.
# Disables ZeroTier if the CPU compilation flags do not specify the "+crypto" extension.
ifeq ($(BR2_aarch64)$(BR2_ARM_CPU_ARMV8A),yy)
    ifneq ($(findstring +crypto,$(BR2_TARGET_OPTIMIZATION)),+crypto)
        DEVILUTIONX_CONF_OPTS += -DDISABLE_ZERO_TIER=ON
    endif
else ifeq ($(BR2_arm),y)
    DEVILUTIONX_CONF_OPTS += -DDISABLE_ZERO_TIER=ON
endif

# ugly hack becuase the is no version in the source file
# and using the git tag doesn't download the submodules properly
define DEVILUTIONX_CLEAR_DL
    if [ -f "$(DL_DIR)/$(DEVILUTIONX_DL_SUBDIR)/$(DEVILUTIONX_SOURCE)" ]; then \
        rm $(DL_DIR)/$(DEVILUTIONX_DL_SUBDIR)/$(DEVILUTIONX_SOURCE); \
    fi
endef

define DEVILUTIONX_INSTALL_TARGET_EVMAPY
	mkdir -p $(TARGET_DIR)/usr/share/evmapy
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/ports/devilutionx/devilutionx.keys \
        $(TARGET_DIR)/usr/share/evmapy
endef

DEVILUTIONX_PRE_DOWNLOAD_HOOKS = DEVILUTIONX_CLEAR_DL
DEVILUTIONX_POST_INSTALL_TARGET_HOOKS = DEVILUTIONX_INSTALL_TARGET_EVMAPY

$(eval $(cmake-package))
