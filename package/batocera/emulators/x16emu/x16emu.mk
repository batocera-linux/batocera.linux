################################################################################
#
# x16emu
#
################################################################################

X16EMU_VERSION = 48
X16EMU_SITE = $(call github,X16Community,x16-emulator,r$(X16EMU_VERSION))
X16EMU_LICENSE = BSD-2-Clause license
X16EMU_LICENSE_FILE = LICENSE

X16EMU_DEPENDENCIES = sdl2

X16EMU_BIOS_SOURCE = Release.R$(X16EMU_VERSION).ROM.Image.zip
X16EMU_EXTRA_DOWNLOADS = \
    https://github.com/X16Community/x16-rom/releases/download/r$(X16EMU_VERSION)/$(X16EMU_BIOS_SOURCE)

define X16EMU_BUILD_CMDS
	$(MAKE) $(TARGET_CONFIGURE_OPTS) \
	SDL_CONFIG=$(STAGING_DIR)/usr/bin/sdl2-config \
	CFLAGS="$(CFLAGS) -I$(STAGING_DIR)/usr/include/SDL2 -Isrc/extern/include" \
	CXXFLAGS="$(CXXFLAGS) -Isrc/extern/ymfm/src" \
	LDFLAGS="-lSDL2 -lm -lz" -C $(@D) all
endef

define X16EMU_INSTALL_TARGET_CMDS
    $(INSTALL) -D -m 0755 $(@D)/x16emu $(TARGET_DIR)/usr/bin/x16emu
endef

define X16EMU_EVMAPY
	mkdir -p $(TARGET_DIR)/usr/share/evmapy
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulators/x16emu/commanderx16.keys \
	    $(TARGET_DIR)/usr/share/evmapy
endef

# Ensure the matching BIOS gets installed for the emulator
define X16EMU_BIOS
    mkdir -p $(@D)/bios
    cd $(@D)/bios && unzip -x -o $(DL_DIR)/$(X16EMU_DL_SUBDIR)/$(X16EMU_BIOS_SOURCE)
	mkdir -p $(TARGET_DIR)/usr/share/batocera/datainit/bios/commanderx16
	cp -f $(@D)/bios/rom.bin $(TARGET_DIR)/usr/share/batocera/datainit/bios/commanderx16
endef

X16EMU_POST_INSTALL_TARGET_HOOKS += X16EMU_EVMAPY
X16EMU_POST_INSTALL_TARGET_HOOKS += X16EMU_BIOS

$(eval $(generic-package))
