################################################################################
#
# MAME
#
################################################################################
# Version.: Release 0.228
MAME_VERSION = mame0228
MAME_SITE = $(call github,mamedev,mame,$(MAME_VERSION))
MAME_DEPENDENCIES = sdl2 zlib libpng fontconfig sqlite jpeg flac rapidjson
MAME_LICENSE = MAME

MAME_CROSS_ARCH = unknown
MAME_CROSS_OPTS =
MAME_CFLAGS =

# Limit number of jobs not to eat too much RAM....
MAME_JOBS = 8

# x86_64 is desktop linux based on X11 and OpenGL
ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_X86_64),y)
MAME_CROSS_ARCH = x86_64
MAME_CROSS_OPTS += PTR64=1
# other archs are embedded, no X11, no OpenGL (only ES)
else
MAME_CROSS_OPTS += NO_X11=1 NO_OPENGL=1 NO_USE_XINPUT=1 NO_USE_BGFX_KHRONOS=1 FORCE_DRC_C_BACKEND=1
endif

# allow cross-architecture compilation with MAME build system
ifeq ($(BR2_aarch64),y)
MAME_CROSS_ARCH = arm64
MAME_CROSS_OPTS += PTR64=1
endif
ifeq ($(BR2_arm),y)
MAME_CROSS_ARCH = arm
MAME_CROSS_OPTS += PTR64=0
# Always enable NEON on 32-bit arm
MAME_CFLAGS += -D__ARM_NEON__ -D__ARM_NEON
endif

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_ODROIDC4),y)
MAME_CFLAGS += -mcpu=cortex-a55 -mtune=cortex-a55
endif

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_ODROIDN2)$(BR2_PACKAGE_BATOCERA_TARGET_VIM3),y)
MAME_CFLAGS += -mcpu=cortex-a73 -mtune=cortex-a73.cortex-a53
endif

define MAME_BUILD_CMDS
	# First, we need to build genie for host
	cd $(@D); \
	PATH="$(HOST_DIR)/bin:$$PATH" \
	$(MAKE) TARGETOS=linux OSD=sdl genie \
	TARGET=mame SUBTARGET=tiny \
	NO_USE_PORTAUDIO=1 NO_X11=1 USE_SDL=0 \
	USE_QTDEBUG=0 DEBUG=0 IGNORE_GIT=1 MPARAM=""

	# Compile emulation target (ARCADE)
	cd $(@D); \
	PATH="$(HOST_DIR)/bin:$$PATH" \
	SYSROOT="$(STAGING_DIR)" \
	CFLAGS="--sysroot=$(STAGING_DIR) $(MAME_CFLAGS)"   \
	LDFLAGS="--sysroot=$(STAGING_DIR)"  MPARAM="" \
	PKG_CONFIG="$(HOST_DIR)/usr/bin/pkg-config --define-prefix" \
	PKG_CONFIG_PATH="$(STAGING_DIR)/usr/lib/pkgconfig" \
	$(MAKE) -j$(MAME_JOBS) TARGETOS=linux OSD=sdl \
	TARGET=mame \
	SUBTARGET=arcade \
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
	OPENMP=1 \
	SDL_INSTALL_ROOT="$(STAGING_DIR)/usr" USE_LIBSDL=1 \
	USE_QTDEBUG=0 DEBUG=0 IGNORE_GIT=1 \
	REGENIE=1 \
	LDOPTS="-lasound -lfontconfig" \
	VERBOSE=1 \
	SYMBOLS=0 \
	STRIP_SYMBOLS=1 \
	TOOLS=1

	# Compile emulation target (MESS)
	cd $(@D); \
	PATH="$(HOST_DIR)/bin:$$PATH" \
	SYSROOT="$(STAGING_DIR)" \
	CFLAGS="--sysroot=$(STAGING_DIR) $(MAME_CFLAGS)"   \
	LDFLAGS="--sysroot=$(STAGING_DIR)"  MPARAM="" \
	PKG_CONFIG="$(HOST_DIR)/usr/bin/pkg-config --define-prefix" \
	PKG_CONFIG_PATH="$(STAGING_DIR)/usr/lib/pkgconfig" \
	$(MAKE) -j$(MAME_JOBS) TARGETOS=linux OSD=sdl \
	TARGET=mame \
	SUBTARGET=batocera \
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
	OPENMP=1 \
	SDL_INSTALL_ROOT="$(STAGING_DIR)/usr" USE_LIBSDL=1 \
	USE_QTDEBUG=0 DEBUG=0 IGNORE_GIT=1 \
	REGENIE=1 \
	LDOPTS="-lasound -lfontconfig" \
	VERBOSE=1 \
	SYMBOLS=0 \
	STRIP_SYMBOLS=1 \
	TOOLS=1
endef

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

	# Install binaries and default distro
        $(INSTALL) -D $(@D)/mamearcade64	$(TARGET_DIR)/usr/bin/mame/mamearcade
        $(INSTALL) -D $(@D)/mamebatocera64	$(TARGET_DIR)/usr/bin/mame/mamemess
        cp $(@D)/COPYING			$(TARGET_DIR)/usr/bin/mame/
        cp $(@D)/README.md			$(TARGET_DIR)/usr/bin/mame/
        cp $(@D)/uismall.bdf			$(TARGET_DIR)/usr/bin/mame/
	cp -R $(@D)/artwork			$(TARGET_DIR)/usr/bin/mame/
	cp -R $(@D)/bgfx			$(TARGET_DIR)/usr/bin/mame/
	cp -R $(@D)/hash			$(TARGET_DIR)/usr/bin/mame/
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
        $(INSTALL) -D $(@D)/romcmp		$(TARGET_DIR)/usr/bin/mame/

        # MAME dev tools skipped
	#$(INSTALL) -D $(@D)/unidasm		$(TARGET_DIR)/usr/bin/mame/
        #$(INSTALL) -D $(@D)/nltool		$(TARGET_DIR)/usr/bin/mame/
        #$(INSTALL) -D $(@D)/nlwav		$(TARGET_DIR)/usr/bin/mame/

	# Delete .po translation files
	find $(TARGET_DIR)/usr/bin/mame/language -name "*.po" -type f -delete

	# Delete bgfx shaders for DX9/DX11/Metal
	rm -Rf $(TARGET_DIR)/usr/bin/mame/bgfx/shaders/metal/
	rm -Rf $(TARGET_DIR)/usr/bin/mame/bgfx/shaders/dx11/
	rm -Rf $(TARGET_DIR)/usr/bin/mame/bgfx/shaders/dx9/

	# Delete useless hash softlist files
	rm -Rf $(TARGET_DIR)/usr/bin/mame/hash/vgmplay.xml
	rm -Rf $(TARGET_DIR)/usr/bin/mame/hash/amigaocs_flop.xml
	rm -Rf $(TARGET_DIR)/usr/bin/mame/hash/dc.xml
	rm -Rf $(TARGET_DIR)/usr/bin/mame/hash/gameboy.xml
	rm -Rf $(TARGET_DIR)/usr/bin/mame/hash/gba.xml
	rm -Rf $(TARGET_DIR)/usr/bin/mame/hash/gbcolor.xml
	rm -Rf $(TARGET_DIR)/usr/bin/mame/hash/megadriv.xml
	rm -Rf $(TARGET_DIR)/usr/bin/mame/hash/nes.hsi
	rm -Rf $(TARGET_DIR)/usr/bin/mame/hash/nes.xml
	rm -Rf $(TARGET_DIR)/usr/bin/mame/hash/psx.xml
	rm -Rf $(TARGET_DIR)/usr/bin/mame/hash/snes.xml
endef

$(eval $(generic-package))
