################################################################################
#
# retroarch
#
################################################################################
#RETROARCH_VERSION = v1.4.1
RETROARCH_VERSION = 76b7235dc5a436c72e86ee5f8efab602359ba6c0

RETROARCH_SITE = $(call github,libretro,RetroArch,$(RETROARCH_VERSION))

RETROARCH_LICENSE = GPLv3+
RETROARCH_CONF_OPTS += --disable-oss --enable-zlib
RETROARCH_DEPENDENCIES = host-pkgconf

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

# RPI 0 and 1
ifeq ($(BR2_arm1176jzf_s),y)
        RETROARCH_CONF_OPTS += --enable-floathard
endif

# RPI 2 and 3
ifeq ($(BR2_cortex_a7),y)
        RETROARCH_CONF_OPTS += --enable-neon --enable-floathard
endif
ifeq ($(BR2_cortex_a8),y)
        RETROARCH_CONF_OPTS += --enable-neon --enable-floathard
endif

# odroid xu4
ifeq ($(BR2_cortex_a15),y)
        RETROARCH_CONF_OPTS += --enable-neon --enable-floathard
endif

# x86 : no option

RETROARCH_CONF_OPTS += --enable-networking

ifeq ($(BR2_PACKAGE_PYTHON3),y)
RETROARCH_CONF_OPTS += --enable-python
RETROARCH_DEPENDENCIES += python
else
RETROARCH_CONF_OPTS += --disable-python
endif

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

ifeq ($(BR2_PACKAGE_LIBXML2),y)
RETROARCH_CONF_OPTS += --enable-libxml2
RETROARCH_DEPENDENCIES += libxml2
else
RETROARCH_CONF_OPTS += --disable-libxml2
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

ifeq ($(BR2_PACKAGE_MALI_OPENGLES_SDK),y)
	RETROARCH_PRE_CONFIGURE_HOOKS += RETROARCH_MALI_FIXUP
	RETROARCH_CONF_OPTS += --enable-opengles --enable-mali_fbdev
endif

define RETROARCH_CONFIGURE_CMDS
	(cd $(@D); rm -rf config.cache; \
		$(TARGET_CONFIGURE_ARGS) \
		$(TARGET_CONFIGURE_OPTS) \
		CFLAGS="$(TARGET_CFLAGS)" \
		LDFLAGS="$(TARGET_LDFLAGS) -lc" \
		CROSS_COMPILE="$(HOST_DIR)/usr/bin/" \
		./configure \
		--prefix=/usr \
		$(RETROARCH_CONF_OPTS) \
	)
endef

define RETROARCH_BUILD_CMDS
	$(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" LD="$(TARGET_LD)" -C $(@D) all
endef

define RETROARCH_INSTALL_TARGET_CMDS
	$(MAKE) CXX="$(TARGET_CXX)" -C $(@D) DESTDIR=$(TARGET_DIR) install
endef

$(eval $(generic-package))

# DEFINITION OF LIBRETRO PLATFORM
LIBRETRO_PLATFORM =
ifeq ($(BR2_ARM_CPU_ARMV6),y)
        LIBRETRO_PLATFORM += armv6
endif

ifeq ($(BR2_cortex_a7),y)
        LIBRETRO_PLATFORM += armv7
endif

ifeq ($(BR2_cortex_a8),y)
        LIBRETRO_PLATFORM += armv8 cortexa8
endif

ifeq ($(BR2_x86_i586),y)
        LIBRETRO_PLATFORM = unix
endif

ifeq ($(BR2_x86_64),y)
        LIBRETRO_PLATFORM = unix
endif

ifeq ($(BR2_cortex_a15),y)
        LIBRETRO_PLATFORM += armv7
endif

ifeq ($(BR2_aarch64),y)
        LIBRETRO_PLATFORM += unix
endif

#ifeq ($(BR2_GCC_TARGET_FLOAT_ABI),"hard")
#        LIBRETRO_PLATFORM += hardfloat
#endif

ifeq ($(BR2_ARM_CPU_HAS_NEON),y)
        LIBRETRO_PLATFORM += neon
endif
