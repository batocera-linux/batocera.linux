################################################################################
#
# MAME (GroovyMAME)
#
################################################################################
# Version: GroovyMAME 0.274 - Switchres 2.21d
MAME_VERSION = gm0274sr221d
MAME_SITE = $(call github,antonioginer,GroovyMAME,$(MAME_VERSION))
MAME_DEPENDENCIES += expat flac fontconfig glm jpeg libpng lua pulseaudio 
MAME_DEPENDENCIES += rapidjson sdl2 sdl2_ttf sqlite zlib

MAME_LICENSE = MAME

MAME_CROSS_ARCH = unknown
MAME_CROSS_OPTS = PRECOMPILE=0
MAME_CFLAGS =
MAME_LDFLAGS =

# Limit number of jobs not to eat too much RAM....
total_memory_kb := $(shell grep MemTotal /proc/meminfo | awk '{print $$2}')
memory_based_jobs := $(shell echo $$(( $(total_memory_kb) / 1024 / 1024 / 2 + 1)))
cpu_threads := $(shell nproc)
jobs := $(shell echo $$(( $(memory_based_jobs) < $(cpu_threads) ? $(memory_based_jobs) : $(cpu_threads) )))
MAME_JOBS := $(jobs)

# Set PTR64 on/off according to architecture
ifeq ($(BR2_ARCH_IS_64),y)
MAME_CROSS_OPTS += PTR64=1
else
MAME_CROSS_OPTS += PTR64=0
# Temp hack for 32-bit architectures : disable WERROR to avoid switchres log warning treated as error
MAME_CROSS_OPTS += NOWERROR=1
endif

# x86_64 is desktop linux based on X11 and OpenGL
ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_X86_64_ANY),y)
MAME_CROSS_ARCH = x86_64
# other archs are embedded, no X11, no OpenGL (only ES)
else
MAME_CROSS_OPTS += NO_X11=1 NO_OPENGL=1 NO_USE_XINPUT=1 NO_USE_BGFX_KHRONOS=1 FORCE_DRC_C_BACKEND=1
endif

# Wayland
ifeq ($(BR2_PACKAGE_BATOCERA_WAYLAND),y)
MAME_CROSS_OPTS += USE_WAYLAND=1
else
MAME_CROSS_OPTS += USE_WAYLAND=0
endif

# Allow cross-architecture compilation with MAME build system
ifeq ($(BR2_aarch64),y)
MAME_CROSS_ARCH = arm64
MAME_CFLAGS += -DEGL_NO_X11=1
endif
ifeq ($(BR2_arm),y)
MAME_CROSS_ARCH = arm
# Always enable NEON on 32-bit arm
MAME_CFLAGS += -D__ARM_NEON__ -D__ARM_NEON -DEGL_NO_X11=1
# workaround for linkage failure using ld on arm 32-bit targets
MAME_LDFLAGS += -fuse-ld=gold -Wl,--long-plt
endif

ifeq ($(BR2_RISCV_64),y)
MAME_CROSS_ARCH = riscv64
# Proper architecture flags
MAME_CFLAGS += -mabi=lp64d -march=rv64imafdczbb_zba -mcpu=sifive-u74
# Force OPTIMIZE level 1 to avoid fatal linking relocation issue so far....
MAME_CROSS_OPTS += OPTIMIZE=2
# Cast alignment warnings cause errors on riscv64
MAME_CFLAGS += -Wno-error=cast-align -Wno-error=unused-function
# Some GCC hacks needed to get riscv64 binary linking
MAME_CFLAGS += -mcmodel=medany -fno-inline-small-functions
MAME_LDFLAGS += -mcmodel=medany
endif

ifeq ($(BR2_cortex_a9),y)
MAME_CFLAGS += -mcpu=cortex-a9 -mtune=cortex-a9 -mfloat-abi=hard
endif

ifeq ($(BR2_cortex_a35),y)
MAME_CFLAGS += -mcpu=cortex-a35 -mtune=cortex-a35
endif

ifeq ($(BR2_cortex_a17),y)
MAME_CFLAGS += -mcpu=cortex-a17 -mtune=cortex-a17 -mfloat-abi=hard
endif

ifeq ($(BR2_cortex_a55),y)
MAME_CFLAGS += -mcpu=cortex-a55 -mtune=cortex-a55
endif

ifeq ($(BR2_cortex_a73_a53),y)
MAME_CFLAGS += -mcpu=cortex-a73.cortex-a53 -mtune=cortex-a73.cortex-a53
endif

ifeq ($(BR2_cortex_a76_a55),y)
MAME_CFLAGS += -mcpu=cortex-a76.cortex-a55 -mtune=cortex-a76.cortex-a55
endif

define MAME_GENIE
	+cd $(@D) ; \
	PATH="$(HOST_DIR)/bin:$$PATH" \
	$(MAKE) TARGETOS=linux OSD=sdl genie \
	TARGET=mame SUBTARGET=tiny \
	NO_USE_PORTAUDIO=1 NO_X11=1 USE_SDL=0 \
	USE_QTDEBUG=0 DEBUG=0 IGNORE_GIT=1 MPARAM=""
endef

MAME_PRE_BUILD_HOOKS += MAME_GENIE

define MAME_BUILD_CMDS
	+cd $(@D) ; \
	PATH="$(HOST_DIR)/bin:$$PATH" \
	SYSROOT="$(STAGING_DIR)" \
	CFLAGS="--sysroot=$(STAGING_DIR) $(MAME_CFLAGS) -fpch-preprocess"   \
	LDFLAGS="--sysroot=$(STAGING_DIR) $(MAME_LDFLAGS)"  MPARAM="" \
	PKG_CONFIG="$(HOST_DIR)/usr/bin/pkg-config --define-prefix" \
	PKG_CONFIG_PATH="$(STAGING_DIR)/usr/lib/pkgconfig" \
	CCACHE_SLOPPINESS="pch_defines,time_macros" \
	$(MAKE) -j$(MAME_JOBS) -l$(MAME_JOBS) TARGETOS=linux OSD=sdl \
	TARGET=mame \
	SUBTARGET=mame \
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

MAME_CONF_INIT = $(TARGET_DIR)/usr/share/batocera/datainit/system/configs/mame/

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
	$(INSTALL) -D $(@D)/mame	$(TARGET_DIR)/usr/bin/mame/mame
	cp $(@D)/COPYING			$(TARGET_DIR)/usr/bin/mame/
	cp $(@D)/README.md			$(TARGET_DIR)/usr/bin/mame/
	cp $(@D)/uismall.bdf		$(TARGET_DIR)/usr/bin/mame/
	cp -R $(@D)/artwork			$(TARGET_DIR)/usr/bin/mame/
	cp -R $(@D)/bgfx			$(TARGET_DIR)/usr/bin/mame/
	cp -R $(@D)/hash			$(TARGET_DIR)/usr/bin/mame/
	cp -R $(@D)/hlsl			$(TARGET_DIR)/usr/bin/mame/
	cp -R $(@D)/ini				$(TARGET_DIR)/usr/bin/mame/
	cp -R $(@D)/keymaps			$(TARGET_DIR)/usr/bin/mame/
	cp -R $(@D)/language		$(TARGET_DIR)/usr/bin/mame/
	cp -R -u $(@D)/plugins		$(TARGET_DIR)/usr/bin/mame/
	# Skip regression tests
	#cp -R $(@D)/regtests		$(TARGET_DIR)/usr/bin/mame/
	cp -R $(@D)/roms			$(TARGET_DIR)/usr/bin/mame/
	cp -R $(@D)/samples			$(TARGET_DIR)/usr/bin/mame/
	cp -R $(@D)/web				$(TARGET_DIR)/usr/bin/mame/

	# MAME tools
	$(INSTALL) -D $(@D)/castool		$(TARGET_DIR)/usr/bin/mame/
	$(INSTALL) -D $(@D)/chdman		$(TARGET_DIR)/usr/bin/mame/
	$(INSTALL) -D $(@D)/floptool	$(TARGET_DIR)/usr/bin/mame/
	$(INSTALL) -D $(@D)/imgtool		$(TARGET_DIR)/usr/bin/mame/
	$(INSTALL) -D $(@D)/jedutil		$(TARGET_DIR)/usr/bin/mame/
	$(INSTALL) -D $(@D)/ldresample	$(TARGET_DIR)/usr/bin/mame/
	$(INSTALL) -D $(@D)/ldverify	$(TARGET_DIR)/usr/bin/mame/
	$(INSTALL) -D $(@D)/romcmp		$(TARGET_DIR)/usr/bin/mame/

	# MAME dev tools skipped
	#$(INSTALL) -D $(@D)/unidasm	$(TARGET_DIR)/usr/bin/mame/
	#$(INSTALL) -D $(@D)/nltool		$(TARGET_DIR)/usr/bin/mame/
	#$(INSTALL) -D $(@D)/nlwav		$(TARGET_DIR)/usr/bin/mame/

	# Delete .po translation files
	find $(TARGET_DIR)/usr/bin/mame/language -name "*.po" -type f -delete

	# Delete bgfx shaders for DX9/DX11/Metal
	rm -Rf $(TARGET_DIR)/usr/bin/mame/bgfx/shaders/metal/
	rm -Rf $(TARGET_DIR)/usr/bin/mame/bgfx/shaders/dx11/

	# Copy extra bgfx shaders
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulators/mame/crt-geom-deluxe-rgb.json \
	    $(TARGET_DIR)/usr/bin/mame/bgfx/chains
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulators/mame/crt-geom-deluxe-composite.json \
	    $(TARGET_DIR)/usr/bin/mame/bgfx/chains

	# Copy blank disk image(s)
	mkdir -p $(TARGET_DIR)/usr/share/mame
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulators/mame/blank.fmtowns \
	    $(TARGET_DIR)/usr/share/mame/blank.fmtowns

	# Copy coin drop plugin
	cp -R -u $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulators/mame/coindrop \
	    $(TARGET_DIR)/usr/bin/mame/plugins

	# Copy data plugin information
	cp -R $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulators/mame/dats \
	    $(TARGET_DIR)/usr/bin/mame/
	cp -R $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulators/mame/history	\
	    $(TARGET_DIR)/usr/bin/mame/

	# gameStop script when exiting a rotated screen (xorg)
	if [ "$(BR2_PACKAGE_XSERVER_XORG_SERVER)" = "y" ]; then \
		mkdir -p $(TARGET_DIR)/usr/share/batocera/configgen/scripts; \
		cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulators/mame/rotation_fix.sh \
			$(TARGET_DIR)/usr/share/batocera/configgen/scripts/rotation_fix.sh; \
	fi

	# Copy user -autoboot_command overrides (batocera.linux/batocera.linux#11706)
	mkdir -p $(MAME_CONF_INIT)/autoload
	cp -R $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulators/mame/autoload \
	    $(MAME_CONF_INIT)
endef

$(eval $(generic-package))
