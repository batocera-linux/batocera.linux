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

MAME_CROSS_ARCH = unknown
MAME_CROSS_OPTS = ""
MAME_TARGET_NAME = mamearcade

# x86_64 is desktop linux based on X11 and OpenGL
ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_X86_64),y)
MAME_CROSS_ARCH = x86_64
MAME_TARGET_NAME = mamearcade64
# other archs are embedded, no X11, no OpenGL (only ES)
else
MAME_CROSS_OPTS = NO_X11=1 NO_OPENGL=1 NO_USE_XINPUT=1 NO_USE_BGFX_KHRONOS=1
endif

# allow cross-architecture compilation with MAME build system
ifeq ($(BR2_aarch64),y)
MAME_CROSS_ARCH = arm64
endif
ifeq ($(BR2_arm),y)
MAME_CROSS_ARCH = arm
endif

define MAME_BUILD_CMDS
	# First, we need to build genie for host
	cd $(@D); \
	$(MAKE) TARGETOS=linux OSD=sdl genie \
	TARGET=mame SUBTARGET=tiny \
	PTR64=1 \
	NO_USE_PORTAUDIO=1 NO_X11=1 USE_SDL=0 \
	USE_QTDEBUG=0 DEBUG=0 IGNORE_GIT=1 MPARAM=""

	# Compile tools target
	cd $(@D); \
	CFLAGS="--sysroot=$(STAGING_DIR)"   \
	CXXFLAGS="--sysroot=$(STAGING_DIR)" \
	LDFLAGS="--sysroot=$(STAGING_DIR)"  MPARAM="" \
	PKG_CONFIG="$(HOST_DIR)/usr/bin/pkg-config --define-prefix" \
	PKG_CONFIG_PATH="$(STAGING_DIR)/usr/lib/pkgconfig" \
	$(MAKE) TARGETOS=linux OSD=sdl \
	TARGET=mame SUBTARGET=tools \
	PTR64=1 \
	OVERRIDE_CC="$(TARGET_CC)" \
	OVERRIDE_CXX="$(TARGET_CXX)" \
	OVERRIDE_LD="$(TARGET_LD)" \
	OVERRIDE_AR="$(TARGET_AR)" \
	OVERRIDE_STRIP="$(TARGET_STRIP)" \
	CROSS_BUILD=1 \
	CROSS_ARCH="$(MAME_CROSS_ARCH)" \
	$(MAME_CROSS_OPTS) \
	NO_USE_PORTAUDIO=1 \
	USE_SYSTEM_LIB_ZLIB=1 \
	USE_SYSTEM_LIB_JPEG=1 \
	USE_SYSTEM_LIB_FLAC=1 \
	USE_SYSTEM_LIB_SQLITE3=1 \
	USE_SYSTEM_LIB_RAPIDJSON=1 \
	SDL_INSTALL_ROOT="$(STAGING_DIR)/usr" USE_LIBSDL=1 \
	USE_QTDEBUG=0 DEBUG=0 IGNORE_GIT=1 \
	REGENIE=1 \
	LDOPTS="-lasound -lfontconfig" \
	VERBOSE=1 \
	SYMBOLS=0 \
	STRIP_SYMBOLS=1 \
	TOOLS=1

	# Compile emulation target
	cd $(@D); \
	CFLAGS="--sysroot=$(STAGING_DIR)"   \
	CXXFLAGS="--sysroot=$(STAGING_DIR)" \
	LDFLAGS="--sysroot=$(STAGING_DIR)"  MPARAM="" \
	PKG_CONFIG="$(HOST_DIR)/usr/bin/pkg-config --define-prefix" \
	PKG_CONFIG_PATH="$(STAGING_DIR)/usr/lib/pkgconfig" \
	$(MAKE) TARGETOS=linux OSD=sdl \
	TARGET=mame \
	SUBTARGET=arcade \
	PTR64=1 \
	OVERRIDE_CC="$(TARGET_CC)" \
	OVERRIDE_CXX="$(TARGET_CXX)" \
	OVERRIDE_LD="$(TARGET_LD)" \
	OVERRIDE_AR="$(TARGET_AR)" \
	OVERRIDE_STRIP="$(TARGET_STRIP)" \
	CROSS_BUILD=1 \
	CROSS_ARCH="$(MAME_CROSS_ARCH)" \
	$(MAME_CROSS_OPTS) \
	NO_USE_PORTAUDIO=1 \
	USE_SYSTEM_LIB_ZLIB=1 \
	USE_SYSTEM_LIB_JPEG=1 \
	USE_SYSTEM_LIB_FLAC=1 \
	USE_SYSTEM_LIB_SQLITE3=1 \
	USE_SYSTEM_LIB_RAPIDJSON=1 \
	SDL_INSTALL_ROOT="$(STAGING_DIR)/usr" USE_LIBSDL=1 \
	USE_QTDEBUG=0 DEBUG=0 IGNORE_GIT=1 \
	REGENIE=1 \
	LDOPTS="-lasound -lfontconfig" \
	VERBOSE=1 \
	SYMBOLS=0 \
	STRIP_SYMBOLS=1 \
	TOOLS=0
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

	# MAME binary and default distro
        $(INSTALL) -D $(@D)/$(MAME_TARGET_NAME)	$(TARGET_DIR)/usr/bin/mame/
        cp $(@D)/COPYING			$(TARGET_DIR)/usr/bin/mame/
        cp $(@D)/README.md			$(TARGET_DIR)/usr/bin/mame/
        cp $(@D)/uismall.bdf			$(TARGET_DIR)/usr/bin/mame/
	cp -R $(@D)/artwork			$(TARGET_DIR)/usr/bin/mame/
	cp -R $(@D)/bgfx			$(TARGET_DIR)/usr/bin/mame/
	# Skip hash folder (software lists for MESS)
	#cp -R $(@D)/hash			$(TARGET_DIR)/usr/bin/mame/
	cp -R $(@D)/hlsl			$(TARGET_DIR)/usr/bin/mame/
	cp -R $(@D)/ini				$(TARGET_DIR)/usr/bin/mame/
	cp -R $(@D)/keymaps			$(TARGET_DIR)/usr/bin/mame/
        cp -R $(@D)/language			$(TARGET_DIR)/usr/bin/mame/
	cp -R $(@D)/plugins			$(TARGET_DIR)/usr/bin/mame/
	# Skip regression tests
	#cp -R $(@D)/regtests			$(TARGET_DIR)/usr/bin/mame/
	cp -R $(@D)/roms			$(TARGET_DIR)/usr/bin/mame/
	cp -R $(@D)/samples			$(TARGET_DIR)/usr/bin/mame/
	cp -R $(@D)/web				$(TARGET_DIR)/usr/bin/mame/

	# MAME tools
        $(INSTALL) -D $(@D)/castool		$(TARGET_DIR)/usr/bin/mame/
        $(INSTALL) -D $(@D)/chdman		$(TARGET_DIR)/usr/bin/mame/
        $(INSTALL) -D $(@D)/floptool		$(TARGET_DIR)/usr/bin/mame/
        $(INSTALL) -D $(@D)/imgtool		$(TARGET_DIR)/usr/bin/mame/
        $(INSTALL) -D $(@D)/jedutil		$(TARGET_DIR)/usr/bin/mame/
        $(INSTALL) -D $(@D)/ldresample		$(TARGET_DIR)/usr/bin/mame/
        $(INSTALL) -D $(@D)/ldverify		$(TARGET_DIR)/usr/bin/mame/
        $(INSTALL) -D $(@D)/nltool		$(TARGET_DIR)/usr/bin/mame/
        $(INSTALL) -D $(@D)/nlwav		$(TARGET_DIR)/usr/bin/mame/
        $(INSTALL) -D $(@D)/romcmp		$(TARGET_DIR)/usr/bin/mame/
        $(INSTALL) -D $(@D)/unidasm		$(TARGET_DIR)/usr/bin/mame/
endef

$(eval $(generic-package))
