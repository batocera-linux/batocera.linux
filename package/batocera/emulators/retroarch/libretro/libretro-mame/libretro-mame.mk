##########################################################™™######################
#
# MAME
#
################################################################################
# Version: Commits on Jan 31, 2021 (0.228)
LIBRETRO_MAME_VERSION =  4b1001771c0394b6cb9f54c19f7d11aeaf0821dd
LIBRETRO_MAME_SITE = $(call github,libretro,mame,$(LIBRETRO_MAME_VERSION))
LIBRETRO_MAME_LICENSE = MAME
LIBRETRO_MAME_DEPENDENCIES = retroarch

# Limit number of jobs not to eat too much RAM....
LIBRETRO_MAME_JOBS=4

ifeq ($(BR2_x86_64),y)
	LIBRETRO_MAME_EXTRA_ARGS += PTR64=1 LIBRETRO_CPU=x86_64 PLATFORM=x86_64
endif

ifeq ($(BR2_i386),y)
	LIBRETRO_MAME_EXTRA_ARGS += PTR64=0 LIBRETRO_CPU=x86 PLATFORM=x86
endif

ifeq ($(BR2_arm),y) 
	LIBRETRO_MAME_EXTRA_ARGS += PTR64=0 LIBRETRO_CPU=arm PLATFORM=arm
	# workaround for asmjit broken build system (arm backend is not public)
	LIBRETRO_MAME_ARCHOPTS += -D__arm__ -DASMJIT_BUILD_X86
endif

ifeq ($(BR2_aarch64),y)
	LIBRETRO_MAME_EXTRA_ARGS += PTR64=1 LIBRETRO_CPU= PLATFORM=arm64
	# workaround for asmjit broken build system (arm backend is not public)
	LIBRETRO_MAME_ARCHOPTS += -D__aarch64__ -DASMJIT_BUILD_X86
endif

ifeq ($(BR2_ENABLE_DEBUG),y)
	LIBRETRO_MAME_EXTRA_ARGS += SYMBOLS=1 SYMLEVEL=2 OPTIMIZE=0
endif

define LIBRETRO_MAME_BUILD_CMDS
	# create some dirs while with parallelism, sometimes it fails because this directory is missing
	mkdir -p $(@D)/build/libretro/obj/x64/libretro/src/osd/libretro/libretro-internal

	$(MAKE) -j$(LIBRETRO_MAME_JOBS) -C $(@D)/ OPENMP=1 REGENIE=1 VERBOSE=1 NOWERROR=1 PYTHON_EXECUTABLE=python3            \
		CONFIG=libretro LIBRETRO_OS="unix" ARCH="" PROJECT="" ARCHOPTS="$(LIBRETRO_MAME_ARCHOPTS)" \
		DISTRO="debian-stable" OVERRIDE_CC="$(TARGET_CC)" OVERRIDE_CXX="$(TARGET_CXX)"             \
		OVERRIDE_LD="$(TARGET_LD)" RANLIB="$(TARGET_RANLIB)" AR="$(TARGET_AR)"                     \
		$(LIBRETRO_MAME_EXTRA_ARGS) CROSS_BUILD=1 TARGET="mame" SUBTARGET="arcade" RETRO=1         \
		OSD="retro" DEBUG=0
endef

define LIBRETRO_MAME_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/mamearcade_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/mame_libretro.so
endef

define LIBRETRO_MAME_INSTALL_STAGING_CMDS
	$(INSTALL) -D $(@D)/mamearcade_libretro.so \
		$(STAGING_DIR)/usr/lib/libretro/mame_libretro.so
endef

$(eval $(generic-package))
