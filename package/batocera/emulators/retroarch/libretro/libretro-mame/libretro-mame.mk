################################################################################
#
# libretro-mame
#
################################################################################

LIBRETRO_MAME_VERSION = lrmame0278
LIBRETRO_MAME_SITE = $(call github,libretro,mame,$(LIBRETRO_MAME_VERSION))
LIBRETRO_MAME_LICENSE = MAME

LIBRETRO_MAME_DEPENDENCIES = alsa-lib retroarch

# Limit number of jobs not to eat too much RAM....
total_memory_kb := $(shell grep MemTotal /proc/meminfo | awk '{print $$2}')
memory_based_jobs := $(shell echo $$(( $(total_memory_kb) / 1024 / 1024 / 2 + 1)))
cpu_threads := $(shell nproc)
jobs := $(shell echo $$(( $(memory_based_jobs) < $(cpu_threads) ? $(memory_based_jobs) : $(cpu_threads) )))
LIBRETRO_MAME_JOBS := $(jobs)

# Determine the correct make target based on architecture
# Default to 'linux' for non-x86 architectures to avoid the -m64 flag issue
LIBRETRO_MAME_ARCH = linux

ifeq ($(BR2_x86_64),y)
LIBRETRO_MAME_EXTRA_ARGS += PTR64=1 LIBRETRO_CPU=x86_64 PLATFORM=x86
LIBRETRO_MAME_ARCH = linux_x64
else ifeq ($(BR2_i386),y)
LIBRETRO_MAME_EXTRA_ARGS += PTR64=0 LIBRETRO_CPU=x86 PLATFORM=x86
LIBRETRO_MAME_ARCH = linux_x86
else ifeq ($(BR2_RISCV_64),y)
LIBRETRO_MAME_EXTRA_ARGS += PTR64=1 LIBRETRO_CPU=riscv64 PLATFORM=riscv64
else ifeq ($(BR2_riscv),y)
LIBRETRO_MAME_EXTRA_ARGS += PTR64=0 LIBRETRO_CPU=riscv PLATFORM=riscv
else ifeq ($(BR2_arm),y)
LIBRETRO_MAME_EXTRA_ARGS += PTR64=0 LIBRETRO_CPU=arm PLATFORM=arm NOASM=1
# workaround for linkage failure using ld on arm 32-bit targets
LIBRETRO_MAME_ARCHOPTS += -fuse-ld=gold -Wl,--long-plt
else ifeq ($(BR2_aarch64),y)
LIBRETRO_MAME_EXTRA_ARGS += PTR64=1 LIBRETRO_CPU= PLATFORM=arm64
# workaround for asmjit broken build system (arm backend is not public)
LIBRETRO_MAME_ARCHOPTS += -D__aarch64__ -DASMJIT_BUILD_X86
endif

ifeq ($(BR2_ENABLE_DEBUG),y)
	# LIBRETRO_MAME_EXTRA_ARGS += SYMBOLS=1 SYMLEVEL=2 OPTIMIZE=0
	LIBRETRO_MAME_EXTRA_ARGS += SYMBOLS=1 OPTIMIZE=0
endif

define LIBRETRO_MAME_BUILD_CMDS
	# create some dirs while with parallelism, sometimes it fails because this directory is missing
	mkdir -p $(@D)/build/libretro/obj/x64/libretro/src/osd/libretro/libretro-internal

	$(MAKE) -j$(LIBRETRO_MAME_JOBS) -l$(LIBRETRO_MAME_JOBS) -C $(@D)/ $(LIBRETRO_MAME_ARCH) \
	    OPENMP=1 REGENIE=1 VERBOSE=1 NOWERROR=1 PYTHON_EXECUTABLE=python3 \
		CONFIG=libretro LIBRETRO_OS="unix" ARCH="" PROJECT="" ARCHOPTS="$(LIBRETRO_MAME_ARCHOPTS)" \
		DISTRO="debian-stable" OVERRIDE_CC="$(TARGET_CC)" OVERRIDE_CXX="$(TARGET_CXX)" \
		OVERRIDE_LD="$(TARGET_LD)" RANLIB="$(TARGET_RANLIB)" AR="$(TARGET_AR)" \
		$(LIBRETRO_MAME_EXTRA_ARGS) CROSS_BUILD=1 TARGET="mame" SUBTARGET="mame" RETRO=1 \
		OSD="retro" DEBUG=0
endef

define LIBRETRO_MAME_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/mame_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/mame_libretro.so
	mkdir -p $(TARGET_DIR)/usr/share/lr-mame/hash
	cp -R $(@D)/hash $(TARGET_DIR)/usr/share/lr-mame

	mkdir -p $(TARGET_DIR)/usr/share/mame
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulators/mame/blank.fmtowns \
	    $(TARGET_DIR)/usr/share/mame/blank.fmtowns

	# Copy coin drop plugin
	mkdir -p $(TARGET_DIR)/usr/bin/mame/
	cp -R -u $(@D)/plugins $(TARGET_DIR)/usr/bin/mame/
	cp -R -u $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulators/mame/coindrop \
	    $(TARGET_DIR)/usr/bin/mame/plugins
endef

define LIBRETRO_MAME_INSTALL_STAGING_CMDS
	$(INSTALL) -D $(@D)/mamearcade_libretro.so \
		$(STAGING_DIR)/usr/lib/libretro/mame_libretro.so
	mkdir -p $(STAGING_DIR)/usr/share/lr-mame/hash
	cp -R $(@D)/hash $(STAGING_DIR)/usr/share/lr-mame
	mkdir -p $(TARGET_DIR)/usr/share/mame
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulators/mame/blank.fmtowns \
	    $(TARGET_DIR)/usr/share/mame/blank.fmtowns
endef

$(eval $(generic-package))
