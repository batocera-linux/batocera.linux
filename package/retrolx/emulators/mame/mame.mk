################################################################################
#
# MAME
#
################################################################################
# Version.: Release 0.232
MAME_VERSION = mame0232
MAME_SITE = $(call github,mamedev,mame,$(MAME_VERSION))
MAME_DEPENDENCIES = sdl2 sdl2_ttf zlib libpng fontconfig sqlite jpeg flac rapidjson expat glm
MAME_LICENSE = MAME

MAME_CROSS_ARCH = unknown
MAME_CROSS_OPTS =
MAME_CFLAGS =

MAME_PKG_DIR = $(TARGET_DIR)/opt/retrolx/mame
MAME_PKG_INSTALL_DIR = /userdata/packages/$(BATOCERA_SYSTEM_ARCH)/mame

# Limit number of jobs not to eat too much RAM....
MAME_JOBS = 12

# x86_64 is desktop linux based on X11 and OpenGL
ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_X86_64),y)
MAME_CROSS_ARCH = x86_64
MAME_CROSS_OPTS += PTR64=1 NO_USE_PULSEAUDIO=1
# other archs are embedded, no X11, no OpenGL (only ES)
else
MAME_CROSS_OPTS += NO_X11=1 NO_OPENGL=1 NO_USE_XINPUT=1 NO_USE_BGFX_KHRONOS=1 FORCE_DRC_C_BACKEND=1 NO_USE_PULSEAUDIO=1 USE_WAYLAND=1
endif

# allow cross-architecture compilation with MAME build system
ifeq ($(BR2_aarch64),y)
MAME_CROSS_ARCH = arm64
MAME_CROSS_OPTS += PTR64=1
MAME_CFLAGS += -DEGL_NO_X11=1
endif
ifeq ($(BR2_arm),y)
MAME_CROSS_ARCH = arm
MAME_CROSS_OPTS += PTR64=0
# Always enable NEON on 32-bit arm
MAME_CFLAGS += -D__ARM_NEON__ -D__ARM_NEON -DEGL_NO_X11=1
endif

ifeq ($(BR2_cortex_a35),y)
MAME_CFLAGS += -mcpu=cortex-a35 -mtune=cortex-a35
endif

ifeq ($(BR2_cortex_a55),y)
MAME_CFLAGS += -mcpu=cortex-a55 -mtune=cortex-a55
endif

ifeq ($(BR2_cortex_a73_a53),y)
MAME_CFLAGS += -mcpu=cortex-a73.cortex-a53 -mtune=cortex-a73.cortex-a53
endif

define MAME_BUILD_CMDS
	# First, we need to build genie for host
	cd $(@D); \
	PATH="$(HOST_DIR)/bin:$$PATH" \
	$(MAKE) TARGETOS=linux OSD=sdl genie \
	TARGET=mame SUBTARGET=tiny \
	NO_USE_PORTAUDIO=1 NO_USE_PULSEAUDIO=1 NO_X11=1 USE_SDL=0 \
	USE_QTDEBUG=0 DEBUG=0 IGNORE_GIT=1 MPARAM=""

	# Compile emulation target (ARCADE)
	cd $(@D); \
	PATH="$(HOST_DIR)/bin:$$PATH" \
	SYSROOT="$(STAGING_DIR)" \
	CFLAGS="--sysroot=$(STAGING_DIR) $(MAME_CFLAGS) -fpch-preprocess"   \
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
	NO_USE_PULSEAUDIO=1 \
	USE_SYSTEM_LIB_ZLIB=1 \
	USE_SYSTEM_LIB_JPEG=1 \
	USE_SYSTEM_LIB_FLAC=1 \
	USE_SYSTEM_LIB_SQLITE3=1 \
	USE_SYSTEM_LIB_RAPIDJSON=1 \
	USE_SYSTEM_LIB_EXPAT=1 \
	USE_SYSTEM_LIB_GLM=1 \
	OPENMP=1 \
	SDL_INSTALL_ROOT="$(STAGING_DIR)/usr" USE_LIBSDL=1 \
	USE_QTDEBUG=0 DEBUG=0 IGNORE_GIT=1 \
	REGENIE=1 \
	LDOPTS="-lasound -lfontconfig" \
	SYMBOLS=0 \
	STRIP_SYMBOLS=1 \
	TOOLS=1

	# Compile emulation target (MESS)
	cd $(@D); \
	PATH="$(HOST_DIR)/bin:$$PATH" \
	SYSROOT="$(STAGING_DIR)" \
	CFLAGS="--sysroot=$(STAGING_DIR) $(MAME_CFLAGS) -fpch-preprocess"   \
	PKG_CONFIG="$(HOST_DIR)/usr/bin/pkg-config --define-prefix" \
	PKG_CONFIG_PATH="$(STAGING_DIR)/usr/lib/pkgconfig" \
	$(MAKE) -j$(MAME_JOBS) TARGETOS=linux OSD=sdl \
	TARGET=mame \
	SUBTARGET=mess \
	OVERRIDE_CC="$(TARGET_CC)" \
	OVERRIDE_CXX="$(TARGET_CXX)" \
	OVERRIDE_LD="$(TARGET_LD)" \
	OVERRIDE_AR="$(TARGET_AR)" \
	OVERRIDE_STRIP="$(TARGET_STRIP)" \
	CROSS_BUILD=1 \
	CROSS_ARCH="$(MAME_CROSS_ARCH)" \
	$(MAME_CROSS_OPTS) \
	NO_USE_PORTAUDIO=1 \
	NO_USE_PULSEAUDIO=1 \
	USE_SYSTEM_LIB_ZLIB=1 \
	USE_SYSTEM_LIB_JPEG=1 \
	USE_SYSTEM_LIB_FLAC=1 \
	USE_SYSTEM_LIB_SQLITE3=1 \
	USE_SYSTEM_LIB_RAPIDJSON=1 \
	USE_SYSTEM_LIB_EXPAT=1 \
	USE_SYSTEM_LIB_GLM=1 \
	OPENMP=1 \
	SDL_INSTALL_ROOT="$(STAGING_DIR)/usr" USE_LIBSDL=1 \
	USE_QTDEBUG=0 DEBUG=0 IGNORE_GIT=1 \
	REGENIE=1 \
	LDOPTS="-lasound -lfontconfig" \
	SYMBOLS=0 \
	STRIP_SYMBOLS=1 \
	TOOLS=1
endef

define MAME_INSTALL_TARGET_CMDS
	# Create specific directories on target to store MAME distro
	mkdir -p $(MAME_PKG_DIR)$(MAME_PKG_INSTALL_DIR)/
	mkdir -p $(MAME_PKG_DIR)$(MAME_PKG_INSTALL_DIR)/ctrlr
	mkdir -p $(MAME_PKG_DIR)$(MAME_PKG_INSTALL_DIR)/docs/legal
	mkdir -p $(MAME_PKG_DIR)$(MAME_PKG_INSTALL_DIR)/docs/man
	mkdir -p $(MAME_PKG_DIR)$(MAME_PKG_INSTALL_DIR)/docs/swlist
	mkdir -p $(MAME_PKG_DIR)$(MAME_PKG_INSTALL_DIR)/hash
	mkdir -p $(MAME_PKG_DIR)$(MAME_PKG_INSTALL_DIR)/ini/examples
	mkdir -p $(MAME_PKG_DIR)$(MAME_PKG_INSTALL_DIR)/ini/presets
	mkdir -p $(MAME_PKG_DIR)$(MAME_PKG_INSTALL_DIR)/language
	mkdir -p $(MAME_PKG_DIR)$(MAME_PKG_INSTALL_DIR)/roms

	# Install binaries and default distro
	$(INSTALL) -D $(@D)/mamearcade		$(MAME_PKG_DIR)$(MAME_PKG_INSTALL_DIR)/mame
	$(INSTALL) -D $(@D)/mess		$(MAME_PKG_DIR)$(MAME_PKG_INSTALL_DIR)/mess
	cp $(@D)/COPYING			$(MAME_PKG_DIR)$(MAME_PKG_INSTALL_DIR)/
	cp $(@D)/README.md			$(MAME_PKG_DIR)$(MAME_PKG_INSTALL_DIR)/
	cp $(@D)/uismall.bdf			$(MAME_PKG_DIR)$(MAME_PKG_INSTALL_DIR)/
	cp -R $(@D)/artwork			$(MAME_PKG_DIR)$(MAME_PKG_INSTALL_DIR)/
	cp -R $(@D)/bgfx			$(MAME_PKG_DIR)$(MAME_PKG_INSTALL_DIR)/
	cp -R $(@D)/hash			$(MAME_PKG_DIR)$(MAME_PKG_INSTALL_DIR)/
	cp -R $(@D)/hlsl			$(MAME_PKG_DIR)$(MAME_PKG_INSTALL_DIR)/
	cp -R $(@D)/ini				$(MAME_PKG_DIR)$(MAME_PKG_INSTALL_DIR)/
	cp -R $(@D)/keymaps			$(MAME_PKG_DIR)$(MAME_PKG_INSTALL_DIR)/
	cp -R $(@D)/language			$(MAME_PKG_DIR)$(MAME_PKG_INSTALL_DIR)/
	cp -R $(@D)/plugins			$(MAME_PKG_DIR)$(MAME_PKG_INSTALL_DIR)/
	cp -R $(@D)/roms			$(MAME_PKG_DIR)$(MAME_PKG_INSTALL_DIR)/
	cp -R $(@D)/samples			$(MAME_PKG_DIR)$(MAME_PKG_INSTALL_DIR)/
	cp -R $(@D)/web				$(MAME_PKG_DIR)$(MAME_PKG_INSTALL_DIR)/

	# MAME tools
	$(INSTALL) -D $(@D)/castool	$(MAME_PKG_DIR)$(MAME_PKG_INSTALL_DIR)/
	$(INSTALL) -D $(@D)/chdman	$(MAME_PKG_DIR)$(MAME_PKG_INSTALL_DIR)/
	$(INSTALL) -D $(@D)/floptool	$(MAME_PKG_DIR)$(MAME_PKG_INSTALL_DIR)/
	$(INSTALL) -D $(@D)/imgtool	$(MAME_PKG_DIR)$(MAME_PKG_INSTALL_DIR)/
	$(INSTALL) -D $(@D)/jedutil	$(MAME_PKG_DIR)$(MAME_PKG_INSTALL_DIR)/
	$(INSTALL) -D $(@D)/ldresample	$(MAME_PKG_DIR)$(MAME_PKG_INSTALL_DIR)/
	$(INSTALL) -D $(@D)/ldverify	$(MAME_PKG_DIR)$(MAME_PKG_INSTALL_DIR)/
	$(INSTALL) -D $(@D)/romcmp	$(MAME_PKG_DIR)$(MAME_PKG_INSTALL_DIR)/

	# Delete bgfx shaders for DX9/DX11/Metal
	rm -Rf $(MAME_PKG_DIR)$(MAME_PKG_INSTALL_DIR)/bgfx/shaders/metal/
	rm -Rf $(MAME_PKG_DIR)$(MAME_PKG_INSTALL_DIR)/bgfx/shaders/dx11/
	rm -Rf $(MAME_PKG_DIR)$(MAME_PKG_INSTALL_DIR)/bgfx/shaders/dx9/

	# Evmapy mapper file
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/retrolx/emulators/mame/mame.mame.keys $(MAME_PKG_DIR)$(MAME_PKG_INSTALL_DIR)/
	
	# Build Pacman package
	cd $(MAME_PKG_DIR) && $(BR2_EXTERNAL_BATOCERA_PATH)/scripts/retrolx-makepkg \
	$(BR2_EXTERNAL_BATOCERA_PATH)/package/retrolx/emulators/mame/PKGINFO \
	$(BATOCERA_SYSTEM_ARCH) $(HOST_DIR)
endef

MAME_POST_INSTALL_TARGET_HOOKS = MAME_MAKEPKG

$(eval $(generic-package))
