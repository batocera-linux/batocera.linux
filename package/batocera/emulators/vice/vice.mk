################################################################################
#
# Vice Emulation
#
################################################################################
# Version.: Dec 24, 2019
VICE_VERSION = 3.4
VICE_SOURCE = vice-$(VICE_VERSION).tar.gz
VICE_SITE = https://freefr.dl.sourceforge.net/project/vice-emu/releases
VICE_LICENSE = GPLv2
VICE_DEPENDENCIES = ffmpeg sdl2 libpng giflib zlib lame alsa-lib jpeg host-xa

VICE_CONF_OPTS += --disable-option-checking

# FFMPEG
VICE_DEPENDENCIES += ffmpeg
VICE_CONF_OPTS += --enable-external-ffmpeg

VICE_CONF_OPTS += --enable-midi
VICE_CONF_OPTS += --enable-lame
VICE_CONF_OPTS += --with-alsa
VICE_CONF_OPTS += --with-zlib
VICE_CONF_OPTS += --with-jpeg
VICE_CONF_OPTS += --with-png
VICE_CONF_OPTS += --enable-x64

VICE_CONF_ENV += LDFLAGS=-lSDL2

define VICE_SDL_CONFIG
	
	mkdir -p $(TARGET_DIR)/usr/share/batocera/datainit/system/configs/vice

	cp -pr $(@D)/data/C64/sdl_hotkeys.vkm \
		$(TARGET_DIR)/usr/share/batocera/datainit/system/configs/vice

	# Commodore 64		
	cp -pr $(@D)/data/C64/sdl_hotkeys.vkm \
		$(TARGET_DIR)/usr/share/batocera/datainit/system/configs/vice/sdl-hotkey-C64.vkm

	# Commodore 128		
	cp -pr $(@D)/data/C128/sdl_hotkeys.vkm \
		$(TARGET_DIR)/usr/share/batocera/datainit/system/configs/vice/sdl_hotkeys-C128.vkm

	# Commodore VIC-20		
	cp -pr $(@D)/data/VIC20/sdl_hotkeys.vkm \
		$(TARGET_DIR)/usr/share/batocera/datainit/system/configs/vice/sdl-hotkey-VIC20.vkm	

endef

VICE_POST_INSTALL_TARGET_HOOKS = VICE_SDL_CONFIG

$(eval $(autotools-package))
