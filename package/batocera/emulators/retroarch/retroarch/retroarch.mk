################################################################################
#
# retroarch
#
################################################################################
# Version.: Commits on Aug 09, 2020
RETROARCH_VERSION = v1.9.0
RETROARCH_SITE = $(call github,libretro,RetroArch,$(RETROARCH_VERSION))
RETROARCH_LICENSE = GPLv3+
RETROARCH_DEPENDENCIES = host-pkgconf dejavu retroarch-assets flac
# install in staging for debugging (gdb)
RETROARCH_INSTALL_STAGING = YES

RETROARCH_CONF_OPTS = --disable-oss --enable-zlib --disable-qt --enable-threads --enable-ozone --enable-xmb --disable-discord
RETROARCH_CONF_OPTS += --enable-flac --enable-lua --enable-networking --enable-translate --enable-rgui

ifeq ($(BR2_PACKAGE_FFMPEG),y)
	RETROARCH_CONF_OPTS += --enable-ffmpeg
	RETROARCH_DEPENDENCIES += ffmpeg
else
	RETROARCH_CONF_OPTS += --disable-ffmpeg
endif

ifeq ($(BR2_PACKAGE_SDL2),y)
	RETROARCH_CONF_OPTS += --enable-sdl2
	RETROARCH_DEPENDENCIES += sdl2
else
	RETROARCH_CONF_OPTS += --disable-sdl2
	ifeq ($(BR2_PACKAGE_SDL),y)
		RETROARCH_CONF_OPTS += --enable-sdl
		RETROARCH_DEPENDENCIES += sdl
	else
		RETROARCH_CONF_OPTS += --disable-sdl
	endif
endif

ifeq ($(BR2_PACKAGE_LIBDRM),y)
	RETROARCH_CONF_OPTS += --enable-kms
endif

ifeq ($(BR2_ARM_FPU_NEON_VFPV4)$(BR2_ARM_FPU_NEON)$(BR2_ARM_FPU_NEON_FP_ARMV8),y)
    RETROARCH_CONF_OPTS += --enable-neon
endif

ifeq ($(BR2_GCC_TARGET_FLOAT_ABI),hard)
    RETROARCH_CONF_OPTS += --enable-floathard
endif

# x86 : no option

ifeq ($(BR2_PACKAGE_XORG7),y)
	RETROARCH_CONF_OPTS += --enable-x11
	RETROARCH_DEPENDENCIES += xserver_xorg-server
else
	RETROARCH_CONF_OPTS += --disable-x11
endif

ifeq ($(BR2_PACKAGE_ALSA_LIB),y)
	RETROARCH_CONF_OPTS += --enable-alsa
	RETROARCH_DEPENDENCIES += alsa-lib
else
	RETROARCH_CONF_OPTS += --disable-alsa
endif

ifeq ($(BR2_PACKAGE_PULSEAUDIO),y)
	RETROARCH_CONF_OPTS += --enable-pulse
	RETROARCH_DEPENDENCIES += pulseaudio
else
	RETROARCH_CONF_OPTS += --disable-pulse
endif

ifeq ($(BR2_PACKAGE_HAS_LIBGLES),y)
	RETROARCH_CONF_OPTS += --enable-opengles
	RETROARCH_DEPENDENCIES += libgles
else
	RETROARCH_CONF_OPTS += --disable-opengles
endif

ifeq ($(BR2_PACKAGE_HAS_LIBEGL),y)
	RETROARCH_CONF_OPTS += --enable-egl
	RETROARCH_DEPENDENCIES += libegl
else
	RETROARCH_CONF_OPTS += --disable-egl
endif

ifeq ($(BR2_PACKAGE_HAS_LIBOPENVG),y)
	RETROARCH_DEPENDENCIES += libopenvg
endif

ifeq ($(BR2_PACKAGE_ZLIB),y)
	RETROARCH_CONF_OPTS += --enable-zlib
	RETROARCH_DEPENDENCIES += zlib
else
	RETROARCH_CONF_OPTS += --disable-zlib
endif

ifeq ($(BR2_PACKAGE_UDEV),y)
	RETROARCH_DEPENDENCIES += udev
endif

ifeq ($(BR2_PACKAGE_FREETYPE),y)
	RETROARCH_CONF_OPTS += --enable-freetype
	RETROARCH_DEPENDENCIES += freetype
else
	RETROARCH_CONF_OPTS += --disable-freetype
endif

define RETROARCH_MALI_FIXUP
	# the type changed with the recent sdk
	$(SED) 's|mali_native_window|fbdev_window|g' $(@D)/gfx/drivers_context/mali_fbdev_ctx.c
endef

ifeq ($(BR2_PACKAGE_MALI_OPENGLES_SDK)$(BR2_PACKAGE_LIBHYBRIS),y)
	RETROARCH_PRE_CONFIGURE_HOOKS += RETROARCH_MALI_FIXUP
	RETROARCH_CONF_OPTS += --enable-opengles --enable-mali_fbdev
endif

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_ODROIDGOA),y)
	RETROARCH_CONF_OPTS += --enable-odroidgo2
	RETROARCH_DEPENDENCIES += librga
else
	RETROARCH_CONF_OPTS += --enable-cdrom
endif


ifeq ($(BR2_PACKAGE_XSERVER_XORG_SERVER),)
	ifeq ($(BR2_PACKAGE_MESA3D_OPENGL_EGL),y)
		RETROARCH_TARGET_CFLAGS += -DEGL_NO_X11
	endif
endif

define RETROARCH_CONFIGURE_CMDS
	(cd $(@D); rm -rf config.cache; \
		$(TARGET_CONFIGURE_ARGS) \
		$(TARGET_CONFIGURE_OPTS) \
		CFLAGS="$(TARGET_CFLAGS) $(RETROARCH_TARGET_CFLAGS)" \
		LDFLAGS="$(TARGET_LDFLAGS) -lc" \
		CROSS_COMPILE="$(HOST_DIR)/usr/bin/" \
		./configure \
		--prefix=/usr \
		$(RETROARCH_CONF_OPTS) \
	)
endef

define RETROARCH_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" LD="$(TARGET_LD)" -C $(@D)/
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" LD="$(TARGET_LD)" -C $(@D)/gfx/video_filters
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" LD="$(TARGET_LD)" -C $(@D)/libretro-common/audio/dsp_filters
endef

define RETROARCH_INSTALL_TARGET_CMDS
	$(MAKE) CXX="$(TARGET_CXX)" -C $(@D) DESTDIR=$(TARGET_DIR) install

	mkdir -p $(TARGET_DIR)/usr/share/video_filters
	cp $(@D)/gfx/video_filters/*.so $(TARGET_DIR)/usr/share/video_filters
	cp $(@D)/gfx/video_filters/*.filt $(TARGET_DIR)/usr/share/video_filters

	mkdir -p $(TARGET_DIR)/usr/share/audio_filters
	cp $(@D)/libretro-common/audio/dsp_filters/*.so $(TARGET_DIR)/usr/share/audio_filters
	cp $(@D)/libretro-common/audio/dsp_filters/*.dsp $(TARGET_DIR)/usr/share/audio_filters
endef

define RETROARCH_INSTALL_STAGING_CMDS
	$(MAKE) CXX="$(TARGET_CXX)" -C $(@D) DESTDIR=$(STAGING_DIR) install
endef

$(eval $(generic-package))

# DEFINITION OF LIBRETRO PLATFORM
LIBRETRO_PLATFORM = unix

ifeq ($(BR2_arm),y)
	ifeq ($(BR2_cortex_a7),y)
		LIBRETRO_PLATFORM += armv7
	endif

	ifeq ($(BR2_cortex_a15),y)
		LIBRETRO_PLATFORM += armv7
	endif

	ifeq ($(BR2_cortex_a17),y)
		LIBRETRO_PLATFORM += armv7
	endif

	ifeq ($(BR2_cortex_a72_a53),y)
		LIBRETRO_PLATFORM += armv7
	endif

	ifeq ($(BR2_cortex_a72),y)
		LIBRETRO_PLATFORM += armv7
	endif
endif

ifeq ($(BR2_ARM_CPU_HAS_NEON),y)
    LIBRETRO_PLATFORM += neon
endif

ifeq ($(BR2_PACKAGE_RPI_USERLAND),y)
	LIBRETRO_PLATFORM += rpi armv
endif

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI2),y)
	LIBRETRO_PLATFORM += rpi2
endif

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI3),y)
	LIBRETRO_PLATFORM += rpi3
endif

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI4),y)
	LIBRETRO_PLATFORM += rpi4
endif

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_ODROIDGOA),y)
	LIBRETRO_PLATFORM += classic_armv8_a35
endif
