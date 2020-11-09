################################################################################
#
# MAME
#
################################################################################
# Version.: Release 0.226
MAME_VERSION = mame0226
MAME_SITE = $(call github,mamedev,mame,$(MAME_VERSION))
MAME_DEPENDENCIES = sdl2 zlib libpng fontconfig sqlite jpeg flac rapidjson
MAME_LICENSE = MAME

define MAME_BUILD_CMDS
	cd $(@D); \
	CFLAGS="--sysroot=$(STAGING_DIR)"   \
	CXXFLAGS="--sysroot=$(STAGING_DIR)" \
	LDFLAGS="--sysroot=$(STAGING_DIR) -lasound -lfontconfig"  \
	PKG_CONFIG="$(HOST_DIR)/usr/bin/pkg-config --define-prefix" \
	PKG_CONFIG_PATH="$(STAGING_DIR)/usr/lib/pkgconfig" \
	$(MAKE) TARGETOS=linux OSD=sdl \
	TARGET=mame \
	SUBTARGET=arcade \
	PTR64=1 \
	OVERRIDE_CC="$(TARGET_CC)" OVERRIDE_CXX="$(TARGET_CXX)" OVERRIDE_LD="$(TARGET_LD)" CROSS_BUILD=1 \
	NO_USE_PORTAUDIO=1 \
	USE_SYSTEM_LIB_ZLIB=1 \
	USE_SYSTEM_LIB_JPEG=1 \
	USE_SYSTEM_LIB_FLAC=1 \
	USE_SYSTEM_LIB_SQLITE3=1 \
	USE_SYSTEM_LIB_RAPIDJSON=1 \
	SDL_INSTALL_ROOT="$(STAGING_DIR)/usr" USE_LIBSDL=1 \
	USE_QTDEBUG=0 DEBUG=0 IGNORE_GIT=1 \
	REGENIE=1 \
	STRIP_SYMBOLS=1 \
	VERBOSE=1 \
	TOOLS=1
endef

# Systems libs disabled for now
#	USE_SYSTEM_LIB_LUA=1 \
#	USE_SYSTEM_LIB_PUGIXML=1 \

define MAME_INSTALL_TARGET_CMDS
	# Create specific directories on target to store MAME distro
	mkdir -p $(TARGET_DIR)/usr/bin/mame/
	mkdir -p $(TARGET_DIR)/usr/bin/mame/ctrlr
	mkdir -p $(TARGET_DIR)/usr/bin/mame/docs/legal
	mkdir -p $(TARGET_DIR)/usr/bin/mame/docs/man
	mkdir -p $(TARGET_DIR)/usr/bin/mame/docs/swlist
	mkdir -p $(TARGET_DIR)/usr/bin/mame/hash
	mkdir -p $(TARGET_DIR)/usr/bin/mame/ini/examples
	mkdir -p $(TARGET_DIR)/usr/bin/mame/ini/presets
	mkdir -p $(TARGET_DIR)/usr/bin/mame/language
	mkdir -p $(TARGET_DIR)/usr/bin/mame/roms

	# MAME binary and minimum files
        $(INSTALL) -D $(@D)/mamearcade64	$(TARGET_DIR)/usr/bin/mame/
        cp $(@D)/COPYING		$(TARGET_DIR)/usr/bin/mame/
        cp $(@D)/uismall.bdf		$(TARGET_DIR)/usr/bin/mame/
        cp $(@D)/roms/dir.txt		$(TARGET_DIR)/usr/bin/mame/roms/
        cp $(@D)/language/LICENSE	$(TARGET_DIR)/usr/bin/mame/language/
        cp $(@D)/language/README.md	$(TARGET_DIR)/usr/bin/mame/language/

	# MAME tools
        $(INSTALL) -D $(@D)/castool	$(TARGET_DIR)/usr/bin/mame/
        $(INSTALL) -D $(@D)/chdman	$(TARGET_DIR)/usr/bin/mame/
        $(INSTALL) -D $(@D)/floptool	$(TARGET_DIR)/usr/bin/mame/
        $(INSTALL) -D $(@D)/imgtool	$(TARGET_DIR)/usr/bin/mame/
        $(INSTALL) -D $(@D)/jedutil	$(TARGET_DIR)/usr/bin/mame/
        $(INSTALL) -D $(@D)/ldresample	$(TARGET_DIR)/usr/bin/mame/
        $(INSTALL) -D $(@D)/ldverify	$(TARGET_DIR)/usr/bin/mame/
        $(INSTALL) -D $(@D)/nltool	$(TARGET_DIR)/usr/bin/mame/
        $(INSTALL) -D $(@D)/nlwav	$(TARGET_DIR)/usr/bin/mame/
        $(INSTALL) -D $(@D)/romcmp	$(TARGET_DIR)/usr/bin/mame/
        $(INSTALL) -D $(@D)/unidasm	$(TARGET_DIR)/usr/bin/mame/

	# Localizations TODO
	#cp -R $(@D)/language/*/*.mo	$(TARGET_DIR)/usr/bin/mame/
endef

$(eval $(generic-package))
