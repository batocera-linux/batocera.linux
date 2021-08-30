################################################################################
#
# pulseaudio utils
#
################################################################################

PULSEAUDIO_UTILS_VERSION = 14.2
PULSEAUDIO_UTILS_SOURCE = pulseaudio-$(PULSEAUDIO_UTILS_VERSION).tar.xz
PULSEAUDIO_UTILS_SITE = https://freedesktop.org/software/pulseaudio/releases
PULSEAUDIO_UTILS_INSTALL_STAGING = YES
PULSEAUDIO_UTILS_LICENSE = LGPL-2.1+ (specific license for modules, see LICENSE file)
PULSEAUDIO_UTILS_LICENSE_FILES = LICENSE GPL LGPL
PULSEAUDIO_UTILS_CONF_OPTS = \
	--disable-default-build-tests \
	--disable-legacy-database-entry-format \
	--disable-manpages \
	--disable-running-from-build-tree

PULSEAUDIO_UTILS_DEPENDENCIES = \
	host-pkgconf libtool libsndfile speex \
	$(TARGET_NLS_DEPENDENCIES) \
	$(if $(BR2_PACKAGE_LIBGLIB2),libglib2) \
	$(if $(BR2_PACKAGE_AVAHI_DAEMON),avahi) \
	$(if $(BR2_PACKAGE_DBUS),dbus) \
	$(if $(BR2_PACKAGE_OPENSSL),openssl) \
	$(if $(BR2_PACKAGE_FFTW_SINGLE),fftw-single) \
	$(if $(BR2_PACKAGE_SYSTEMD),systemd)

ifeq ($(BR2_PACKAGE_LIBSAMPLERATE),y)
PULSEAUDIO_UTILS_CONF_OPTS += --enable-samplerate
PULSEAUDIO_UTILS_DEPENDENCIES += libsamplerate
else
PULSEAUDIO_UTILS_CONF_OPTS += --disable-samplerate
endif

ifeq ($(BR2_PACKAGE_GDBM),y)
PULSEAUDIO_UTILS_CONF_OPTS += --with-database=gdbm --with-database=simple
PULSEAUDIO_UTILS_DEPENDENCIES += gdbm
else
PULSEAUDIO_UTILS_CONF_OPTS += --with-database=simple
endif

ifeq ($(BR2_PACKAGE_JACK2),y)
PULSEAUDIO_UTILS_CONF_OPTS += --enable-jack
PULSEAUDIO_UTILS_DEPENDENCIES += jack2
else
PULSEAUDIO_UTILS_CONF_OPTS += --disable-jack
endif

ifeq ($(BR2_PACKAGE_LIBATOMIC_OPS),y)
PULSEAUDIO_UTILS_DEPENDENCIES += libatomic_ops
ifeq ($(BR2_sparc_v8)$(BR2_sparc_leon3),y)
PULSEAUDIO_UTILS_CONF_ENV += CFLAGS="$(TARGET_CFLAGS) -DAO_NO_SPARC_V9"
endif
endif

ifeq ($(BR2_PACKAGE_ORC),y)
PULSEAUDIO_UTILS_DEPENDENCIES += orc
PULSEAUDIO_UTILS_CONF_ENV += ORCC=$(HOST_DIR)/bin/orcc
PULSEAUDIO_UTILS_CONF_OPTS += --enable-orc
else
PULSEAUDIO_UTILS_CONF_OPTS += --disable-orc
endif

ifeq ($(BR2_PACKAGE_LIBCAP),y)
PULSEAUDIO_UTILS_DEPENDENCIES += libcap
PULSEAUDIO_UTILS_CONF_OPTS += --with-caps
else
PULSEAUDIO_UTILS_CONF_OPTS += --without-caps
endif

# gtk3 support needs X11 backend
ifeq ($(BR2_PACKAGE_LIBGTK3_X11),y)
PULSEAUDIO_UTILS_DEPENDENCIES += libgtk3
PULSEAUDIO_UTILS_CONF_OPTS += --enable-gtk3
else
PULSEAUDIO_UTILS_CONF_OPTS += --disable-gtk3
endif

ifeq ($(BR2_PACKAGE_LIBSOXR),y)
PULSEAUDIO_UTILS_CONF_OPTS += --with-soxr
PULSEAUDIO_UTILS_DEPENDENCIES += libsoxr
else
PULSEAUDIO_UTILS_CONF_OPTS += --without-soxr
endif

ifeq ($(BR2_PACKAGE_BLUEZ5_UTILS)$(BR2_PACKAGE_SBC),yy)
PULSEAUDIO_UTILS_CONF_OPTS += --enable-bluez5
PULSEAUDIO_UTILS_DEPENDENCIES += bluez5_utils sbc
else
PULSEAUDIO_UTILS_CONF_OPTS += --disable-bluez5
endif

ifeq ($(BR2_PACKAGE_HAS_UDEV),y)
PULSEAUDIO_UTILS_CONF_OPTS += --enable-udev
PULSEAUDIO_UTILS_DEPENDENCIES += udev
else
PULSEAUDIO_UTILS_CONF_OPTS += --disable-udev
endif

ifeq ($(BR2_PACKAGE_WEBRTC_AUDIO_PROCESSING),y)
PULSEAUDIO_UTILS_CONF_OPTS += --enable-webrtc-aec
PULSEAUDIO_UTILS_DEPENDENCIES += webrtc-audio-processing
else
PULSEAUDIO_UTILS_CONF_OPTS += --disable-webrtc-aec
endif

# neon intrinsics not available with float-abi=soft
ifeq ($(BR2_ARM_SOFT_FLOAT),)
ifeq ($(BR2_ARM_CPU_HAS_NEON),y)
PULSEAUDIO_UTILS_USE_NEON = y
endif
endif

ifeq ($(PULSEAUDIO_UTILS_USE_NEON),y)
PULSEAUDIO_UTILS_CONF_OPTS += --enable-neon-opt=yes
else
PULSEAUDIO_UTILS_CONF_OPTS += --enable-neon-opt=no
endif

# pulseaudio alsa backend needs pcm/mixer apis
ifeq ($(BR2_PACKAGE_ALSA_LIB_PCM)$(BR2_PACKAGE_ALSA_LIB_MIXER),yy)
PULSEAUDIO_UTILS_DEPENDENCIES += alsa-lib
PULSEAUDIO_UTILS_CONF_OPTS += --enable-alsa
else
PULSEAUDIO_UTILS_CONF_OPTS += --disable-alsa
endif

ifeq ($(BR2_PACKAGE_LIBXCB)$(BR2_PACKAGE_XLIB_LIBSM)$(BR2_PACKAGE_XLIB_LIBXTST),yyy)
PULSEAUDIO_UTILS_DEPENDENCIES += libxcb xlib_libSM xlib_libXtst

# .desktop file generation needs nls support, so fake it for !locale builds
# https://bugs.freedesktop.org/show_bug.cgi?id=54658
ifeq ($(BR2_SYSTEM_ENABLE_NLS),)
define PULSEAUDIO_UTILS_FIXUP_DESKTOP_FILES
	cp $(@D)/src/daemon/pulseaudio.desktop.in \
		$(@D)/src/daemon/pulseaudio.desktop
endef
PULSEAUDIO_UTILS_POST_PATCH_HOOKS += PULSEAUDIO_UTILS_FIXUP_DESKTOP_FILES
endif

else
PULSEAUDIO_UTILS_CONF_OPTS += --disable-x11
endif

define PULSEAUDIO_UTILS_INSTALL_TARGET_CMDS
	# pactl
	cp $(@D)/src/pactl $(TARGET_DIR)/usr/bin/
	
	# libpulse
	cp $(@D)/src/.libs/libpulse.so $(TARGET_DIR)/usr/lib/
	ln -sf libpulse.so $(TARGET_DIR)/usr/lib/libpulse.so.0
	cp $(@D)/src/.libs/libpulsecommon-$(PULSEAUDIO_UTILS_VERSION).so $(TARGET_DIR)/usr/lib/
	cp $(@D)/src/.libs/libpulse-simple.so $(TARGET_DIR)/usr/lib/
	ln -sf libpulse-simple.so $(TARGET_DIR)/usr/lib/libpulse-simple.so.0
endef

$(eval $(autotools-package))
