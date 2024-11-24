################################################################################
#
# libretro-same-cdi
#
################################################################################
# Version: Commits on Mar 1, 2023
LIBRETRO_SAME_CDI_VERSION = 54cf493c2dee4c46666059c452f8aaaa0bd7c8e0
LIBRETRO_SAME_CDI_SITE = $(call github,libretro,same_cdi,$(LIBRETRO_SAME_CDI_VERSION))
LIBRETRO_SAME_CDI_LICENSE = GPL

ifeq ($(BR2_x86_64),y)
LIBRETRO_SAME_CDI_EXTRA_ARGS += PTR64=1 LIBRETRO_CPU=x86_64 PLATFORM=x86_64
else ifeq ($(BR2_aarch64),y)
LIBRETRO_SAME_CDI_EXTRA_ARGS += PTR64=1 LIBRETRO_CPU= PLATFORM=arm64 ARCHITECTURE= NOASM=1
endif

define LIBRETRO_SAME_CDI_BUILD_CMDS
	# First, we need to build genie for host
	cd $(@D); \
	PATH="$(HOST_DIR)/bin:$$PATH" \
	$(MAKE) TARGETOS=linux OSD=sdl genie \
	TARGET=mame SUBTARGET=tiny \
	NO_USE_PORTAUDIO=1 NO_X11=1 USE_SDL=0 \
	USE_QTDEBUG=0 DEBUG=0 IGNORE_GIT=1 MPARAM=""

	# Then build lr-same-cdi for target
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" \
	$(LIBRETRO_SAME_CDI_EXTRA_ARGS) \
	GIT_VERSION="" -C $(@D) -f Makefile.libretro
endef

define LIBRETRO_SAME_CDI_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/same_cdi_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/same_cdi_libretro.so
endef

$(eval $(generic-package))
