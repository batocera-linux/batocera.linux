################################################################################
#
# retroarch
#
################################################################################
#RETROARCH_VERSION = 2755abc14fe25b9f32e145dcf6ec5c9569640eb8 for rpi1

#ifeq ($(BR2_cortex_a7),y)
#	RETROARCH_VERSION = 79f2a92202f62b51e7ed8f6fb089cb38ce0fede9
#else
#	RETROARCH_VERSION = 2755abc14fe25b9f32e145dcf6ec5c9569640eb8
#endif

RETROARCH_VERSION = a31192c55a6661b0a25dd5792cee93c3f828b8fa
RETROARCH_SITE = https://github.com/libretro/RetroArch.git
RETROARCH_SITE_METHOD = git
RETROARCH_LICENSE = GPLv3+
RETROARCH_CONF_OPTS += --disable-oss --enable-floathard --enable-zlib
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

ifeq ($(BR2_cortex_a7),y)
        RETROARCH_CONF_OPTS += --enable-neon --enable-networking --enable-netplay
endif

ifeq ($(BR2_PACKAGE_PYTHON3),y)
RETROARCH_CONF_OPTS += --enable-python
RETROARCH_DEPENDENCIES += python
else
RETROARCH_CONF_OPTS += --disable-python
endif

ifeq ($(BR2_PACKAGE_XORG7),y)
RETROARCH_CONF_OPTS += --enable-x11
RETROARCH_DEPENDENCIES += x11r7
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
RETROARCH_CONF_OPTS += --enable-gles
RETROARCH_DEPENDENCIES += libgles
else
RETROARCH_CONF_OPTS += --disable-gles
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
	$(MAKE) CC="$(TARGET_CC)" LD="$(TARGET_LD)" -C $(@D) all
endef

define RETROARCH_INSTALL_TARGET_CMDS
	$(MAKE) -C $(@D) DESTDIR=$(TARGET_DIR) install
endef

$(eval $(generic-package))

LIBRETRO_PLATFORM =
ifeq ($(BR2_ARM_CPU_ARMV6),y)
        LIBRETRO_PLATFORM += armv6
endif

ifeq ($(BR2_cortex_a7),y)
        LIBRETRO_PLATFORM += armv7
endif

ifeq ($(BR2_GCC_TARGET_FLOAT_ABI),"hard")
        LIBRETRO_PLATFORM += hardfloat
endif

ifeq ($(BR2_ARM_CPU_HAS_NEON),y)
        LIBRETRO_PLATFORM += neon
endif
