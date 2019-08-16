##########################################################™™######################
#
# MAME
#
################################################################################
# Version.: Commits on Aug 4, 2019 (0.212)
LIBRETRO_MAME_VERSION = d69ac66741ae89b27d843bc645944bdc1f37265f
LIBRETRO_MAME_SITE = $(call github,libretro,mame,$(LIBRETRO_MAME_VERSION))
LIBRETRO_MAME_LICENSE = MAME


ifeq ($(BR2_x86_64),y)
	LIBRETRO_MAME_EXTRA_ARGS += PTR64=1 LIBRETRO_CPU=x86_64 PLATFORM=x86_64
endif

ifeq ($(BR2_i386),y)
	LIBRETRO_MAME_EXTRA_ARGS += PTR64=0 LIBRETRO_CPU=x86 PLATFORM=x86
endif

ifeq ($(BR2_arm),y)
	LIBRETRO_MAME_EXTRA_ARGS += PTR64=0 LIBRETRO_CPU=arm PLATFORM=arm
	LIBRETRO_MAME_ARCHOPTS += -D__arm__
endif

define LIBRETRO_MAME_BUILD_CMDS
	$(MAKE) -C $(@D)/ REGENIE=1 VERBOSE=1 NOWERROR=1 PYTHON_EXECUTABLE=python2                     \
		CONFIG=libretro LIBRETRO_OS="unix" ARCH="" PROJECT="" ARCHOPTS="$(LIBRETRO_MAME_ARCHOPTS)" \
		DISTRO="debian-stable" OVERRIDE_CC="$(TARGET_CC)" OVERRIDE_CXX="$(TARGET_CXX)"             \
		OVERRIDE_LD="$(TARGET_LD)" RANLIB="$(TARGET_RANLIB)" AR="$(TARGET_AR)"                      \
		$(LIBRETRO_MAME_EXTRA_ARGS) CROSS_BUILD=1 TARGET="mame" SUBTARGET="arcade" RETRO=1         \
		OSD="retro"
endef

define LIBRETRO_MAME_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/mamearcade_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/mame_libretro.so
endef

$(eval $(generic-package))
