################################################################################
#
# retroarch
#
################################################################################

RETROARCH_VERSION = 4b74434a30c534c763b60ba4cc16f6a94a611c5f
RETROARCH_SITE = $(call github,libretro,RetroArch,$(RETROARCH_VERSION))
RETROARCH_LICENSE = GPLv3+
RETROARCH_DEPENDENCIES = host-pkgconf dejavu retroarch-assets flac noto-cjk-fonts
# install in staging for debugging (gdb)
RETROARCH_INSTALL_STAGING = YES

$(eval $(call register,libretro.emulator.yml))
$(eval $(call register-if-kconfig,BR2_PACKAGE_BATOCERA_VULKAN,gfxbackend.libretro.emulator.yml))

RETROARCH_CONF_OPTS = --prefix=/usr --disable-oss --disable-qt --enable-threads \
    --enable-ozone --enable-xmb --disable-discord --enable-flac --enable-lua \
    --enable-networking --enable-translate --enable-rgui --disable-cdrom \
    --enable-zlib --disable-builtinzlib

ifeq ($(BR2_ENABLE_DEBUG),y)
    RETROARCH_CONF_OPTS += --enable-debug
endif

ifeq ($(BR2_PACKAGE_ALSA_LIB),y)
    RETROARCH_CONF_OPTS += --enable-alsa
    RETROARCH_DEPENDENCIES += alsa-lib
else
    RETROARCH_CONF_OPTS += --disable-alsa
endif

ifeq ($(BR2_PACKAGE_FFMPEG),y)
    RETROARCH_CONF_OPTS += --enable-ffmpeg
    RETROARCH_DEPENDENCIES += ffmpeg
else
    RETROARCH_CONF_OPTS += --disable-ffmpeg
endif

ifeq ($(BR2_PACKAGE_FREETYPE),y)
    RETROARCH_CONF_OPTS += --enable-freetype
    RETROARCH_DEPENDENCIES += freetype
else
    RETROARCH_CONF_OPTS += --disable-freetype
endif

ifeq ($(BR2_PACKAGE_LIBDRM),y)
    RETROARCH_CONF_OPTS += --enable-kms
endif

ifeq ($(BR2_PACKAGE_HAS_LIBOPENVG),y)
    RETROARCH_DEPENDENCIES += libopenvg

endif

ifeq ($(BR2_PACKAGE_PULSEAUDIO),y)
    RETROARCH_CONF_OPTS += --enable-pulse
    RETROARCH_DEPENDENCIES += pulseaudio
else
    RETROARCH_CONF_OPTS += --disable-pulse
endif

ifeq ($(BR2_PACKAGE_SDL2),y)
    RETROARCH_CONF_OPTS += --enable-sdl2
    RETROARCH_DEPENDENCIES += sdl2
else ifeq ($(BR2_PACKAGE_SDL),y)
    RETROARCH_CONF_OPTS += --enable-sdl
    RETROARCH_DEPENDENCIES += sdl
else
    RETROARCH_CONF_OPTS += --disable-sdl2 --disable-sdl
endif

ifeq ($(BR2_PACKAGE_UDEV),y)
    RETROARCH_DEPENDENCIES += udev
endif

ifeq ($(BR2_PACKAGE_WAYLAND),y)
    RETROARCH_CONF_OPTS += --enable-wayland
else
    RETROARCH_CONF_OPTS += --disable-wayland
endif

ifeq ($(BR2_PACKAGE_XSERVER_XORG_SERVER),y)
    RETROARCH_CONF_OPTS += --enable-x11
    RETROARCH_DEPENDENCIES += xserver_xorg-server
else
    RETROARCH_CONF_OPTS += --disable-x11
endif

ifeq ($(BR2_PACKAGE_ZLIB),y)
    RETROARCH_CONF_OPTS += --disable-builtinzlib --enable-zlib
    RETROARCH_DEPENDENCIES += zlib
else
    RETROARCH_CONF_OPTS += --disable-zlib
endif

ifeq ($(BR2_x86_64),y)
    RETROARCH_CONF_OPTS += --enable-opengl --disable-opengles --disable-opengles3
    RETROARCH_DEPENDENCIES += libgl
else ifeq ($(BR2_PACKAGE_BATOCERA_GLES3),y)
    # don't enable --enable-opengles3_2, breaks lr-swanstation
    RETROARCH_CONF_OPTS += --disable-opengl --enable-opengles --enable-opengles3 --enable-opengles3_1
    RETROARCH_DEPENDENCIES += libgles
else ifeq ($(BR2_PACKAGE_BATOCERA_GLES2),y)
    RETROARCH_CONF_OPTS += --disable-opengl --enable-opengles
    RETROARCH_DEPENDENCIES += libgles
endif

ifeq ($(BR2_PACKAGE_HAS_LIBEGL),y)
    RETROARCH_CONF_OPTS += --enable-egl
    RETROARCH_DEPENDENCIES += libegl
endif

ifeq ($(BR2_PACKAGE_VULKAN_LOADER)$(BR2_PACKAGE_VULKAN_HEADERS),yy)
    RETROARCH_CONF_OPTS += --enable-vulkan
    RETROARCH_DEPENDENCIES += vulkan-headers vulkan-loader slang-shaders
endif

ifeq ($(BR2_PACKAGE_GLSLANG),y)
    RETROARCH_CONF_OPTS += --disable-builtinglslang --enable-glslang
    RETROARCH_DEPENDENCIES += glslang
endif

ifeq ($(BR2_PACKAGE_RPI_USERLAND),y)
    RETROARCH_CONF_OPTS += --enable-videocore
endif

ifeq ($(BR2_ARM_FPU_NEON_VFPV4)$(BR2_ARM_FPU_NEON)$(BR2_ARM_FPU_NEON_FP_ARMV8),y)
    RETROARCH_CONF_OPTS += --enable-neon
endif

ifeq ($(BR2_GCC_TARGET_FLOAT_ABI),hard)
    RETROARCH_CONF_OPTS += --enable-floathard
endif

ifeq ($(BR2_PACKAGE_ROCKCHIP_RGA),y)
    RETROARCH_DEPENDENCIES += rockchip-rga
endif

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RK3326),y)
     RETROARCH_CONF_OPTS += --enable-odroidgo2
endif

ifeq ($(BR2_PACKAGE_XSERVER_XORG_SERVER),)
    ifeq ($(BR2_PACKAGE_MESA3D_OPENGL_EGL),y)
        RETROARCH_TARGET_CFLAGS += -DEGL_NO_X11
    endif
endif

ifeq ($(BR2_riscv),y)
	RETROARCH_TARGET_CFLAGS += -DMESA_EGL_NO_X11_HEADERS=1
endif

define RETROARCH_CONFIGURE_CMDS
	(cd $(@D); rm -rf config.cache; \
		$(TARGET_CONFIGURE_ARGS) \
		$(TARGET_CONFIGURE_OPTS) \
		CFLAGS="$(TARGET_CFLAGS) $(RETROARCH_TARGET_CFLAGS)" \
		LDFLAGS="$(TARGET_LDFLAGS) $(RETROARCH_TARGET_LDFLAGS) -lc" \
		CROSS_COMPILE="$(HOST_DIR)/usr/bin/" \
		./configure \
		$(RETROARCH_CONF_OPTS) \
	)
endef

define RETROARCH_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" \
        LD="$(TARGET_LD)" -C $(@D)/
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" \
        LD="$(TARGET_LD)" -C $(@D)/gfx/video_filters
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" \
        LD="$(TARGET_LD)" -C $(@D)/libretro-common/audio/dsp_filters
endef

define RETROARCH_INSTALL_TARGET_CMDS
	$(MAKE) CXX="$(TARGET_CXX)" -C $(@D) DESTDIR=$(TARGET_DIR) install

	mkdir -p $(TARGET_DIR)/usr/share/video_filters
	cp $(@D)/gfx/video_filters/*.so $(TARGET_DIR)/usr/share/video_filters
	cp $(@D)/gfx/video_filters/*.filt $(TARGET_DIR)/usr/share/video_filters

	mkdir -p $(TARGET_DIR)/usr/share/audio_filters
	cp $(@D)/libretro-common/audio/dsp_filters/*.so \
        $(TARGET_DIR)/usr/share/audio_filters
	cp $(@D)/libretro-common/audio/dsp_filters/*.dsp \
        $(TARGET_DIR)/usr/share/audio_filters
endef

define RETROARCH_INSTALL_STAGING_CMDS
	$(MAKE) CXX="$(TARGET_CXX)" -C $(@D) DESTDIR=$(STAGING_DIR) install
endef

$(eval $(generic-package))
$(eval $(emulator-info-package))

LIBRETRO_PLATFORM = unix
ifeq ($(BR2_arm),y)
    LIBRETRO_PLATFORM += armv7
endif
ifeq ($(BR2_aarch64),y)
    LIBRETRO_PLATFORM += arm64
endif
ifeq ($(BR2_ARM_CPU_HAS_NEON),y)
    LIBRETRO_PLATFORM += neon
endif
ifeq ($(BR2_PACKAGE_RPI_USERLAND),y)
    LIBRETRO_PLATFORM += rpi armv
endif

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2836),y)
    LIBRETRO_PLATFORM += rpi2
endif

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2837),y)
    LIBRETRO_PLATFORM += rpi3_64
endif

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2711),y)
    LIBRETRO_PLATFORM += rpi4_64
endif

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2712),y)
    LIBRETRO_PLATFORM += rpi5_64
endif
