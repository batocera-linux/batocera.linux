################################################################################
#
# kodi
#
################################################################################

# When updating the version, please also update kodi-jsonschemabuilder
# and kodi-texturepacker
KODI18_VERSION = 18.6-Leia
KODI18_SITE = $(call github,xbmc,xbmc,$(KODI18_VERSION))

ifeq ($(BR2_PACKAGE_KODI18_PLATFORM_RBPI),y)
KODI18_VERSION = newclock5_18.6-Leia
KODI18_SITE = $(call github,popcornmix,xbmc,$(KODI18_VERSION))
endif


KODI18_LICENSE = GPL-2.0
KODI18_LICENSE_FILES = LICENSE.md
# needed for binary addons
KODI18_INSTALL_STAGING = YES
# kodi18 recommends building out-of-source
KODI18_SUPPORTS_IN_SOURCE_BUILD = NO
KODI18_DEPENDENCIES = \
	expat \
	flatbuffers \
	fmt \
	fontconfig \
	freetype \
	fstrcmp \
	gnutls \
	host-flatbuffers \
	host-gawk \
	host-gettext \
	host-gperf \
	host-kodi-jsonschemabuilder \
	host-kodi-texturepacker \
	host-nasm \
	host-swig \
	host-xmlstarlet \
	libass \
	libcdio \
	libcrossguid \
	libcurl \
	libfribidi \
	libplist \
	libsamplerate \
	lzo \
	ncurses \
	openssl \
	pcre \
	python \
	rapidjson \
	sqlite \
	taglib \
	tinyxml \
	zlib

# taken from tools/depends/target/ffmpeg/FFMPEG-VERSION
KODI18_FFMPEG_VERSION = 4.0.4-Leia-18.4
KODI18_LIBDVDCSS_VERSION = 1.4.2-Leia-Beta-5
KODI18_LIBDVDNAV_VERSION = 6.0.0-Leia-Alpha-3
KODI18_LIBDVDREAD_VERSION = 6.0.0-Leia-Alpha-3
KODI18_EXTRA_DOWNLOADS += \
	$(call github,xbmc,FFmpeg,$(KODI18_FFMPEG_VERSION))/kodi-ffmpeg-$(KODI18_FFMPEG_VERSION).tar.gz \
	$(call github,xbmc,libdvdcss,$(KODI18_LIBDVDCSS_VERSION))/kodi-libdvdcss-$(KODI18_LIBDVDCSS_VERSION).tar.gz \
	$(call github,xbmc,libdvdnav,$(KODI18_LIBDVDNAV_VERSION))/kodi-libdvdnav-$(KODI18_LIBDVDNAV_VERSION).tar.gz \
	$(call github,xbmc,libdvdread,$(KODI18_LIBDVDREAD_VERSION))/kodi-libdvdread-$(KODI18_LIBDVDREAD_VERSION).tar.gz


define KODI18_CPLUFF_AUTOCONF
	cd $(KODI18_SRCDIR)/lib/cpluff && PATH=$(HOST_DIR)/bin:$$PATH ./autogen.sh
endef
KODI18_PRE_CONFIGURE_HOOKS += KODI18_CPLUFF_AUTOCONF
KODI18_DEPENDENCIES += host-automake host-autoconf host-libtool

KODI18_CONF_OPTS += \
	-DCMAKE_C_FLAGS="$(TARGET_CFLAGS) $(KODI18_C_FLAGS)" \
	-DCMAKE_CXX_FLAGS="$(TARGET_CXXFLAGS) $(KODI18_CXX_FLAGS)" \
	-DENABLE_APP_AUTONAME=OFF \
	-DENABLE_CCACHE=OFF \
	-DENABLE_DVDCSS=ON \
	-DENABLE_INTERNAL_CROSSGUID=OFF \
	-DENABLE_INTERNAL_FFMPEG=ON \
	-DENABLE_INTERNAL_FLATBUFFERS=OFF \
	-DFFMPEG_URL=$(KODI18_DL_DIR)/kodi-ffmpeg-$(KODI18_FFMPEG_VERSION).tar.gz \
	-DKODI18_DEPENDSBUILD=OFF \
	-DENABLE_LDGOLD=OFF \
	-DNATIVEPREFIX=$(HOST_DIR) \
	-DDEPENDS_PATH=$(STAGING_DIR)/usr \
	-DWITH_JSONSCHEMABUILDER=$(HOST_DIR)/bin/JsonSchemaBuilder \
	-DWITH_TEXTUREPACKER=$(HOST_DIR)/bin/TexturePacker \
	-DLIBDVDCSS_URL=$(KODI18_DL_DIR)/kodi-libdvdcss-$(KODI18_LIBDVDCSS_VERSION).tar.gz \
	-DLIBDVDNAV_URL=$(KODI18_DL_DIR)/kodi-libdvdnav-$(KODI18_LIBDVDNAV_VERSION).tar.gz \
	-DLIBDVDREAD_URL=$(KODI18_DL_DIR)/kodi-libdvdread-$(KODI18_LIBDVDREAD_VERSION).tar.gz

ifeq ($(BR2_ENABLE_LOCALE),)
KODI18_DEPENDENCIES += libiconv
endif

ifeq ($(BR2_PACKAGE_KODI18_PLATFORM_RBPI),y)
# These CPU-specific options are only used on rbpi:
# https://github.com/xbmc/xbmc/blob/Krypton/project/cmake/scripts/rbpi/ArchSetup.cmake#L13
ifeq ($(BR2_arm1176jzf_s)$(BR2_cortex_a7)$(BR2_cortex_a53),y)
KODI18_CONF_OPTS += -DWITH_CPU="$(GCC_TARGET_CPU)"
endif
else ifeq ($(BR2_arceb)$(BR2_arcle),y)
KODI18_CONF_OPTS += -DWITH_ARCH=arc -DWITH_CPU=arc
else ifeq ($(BR2_armeb),y)
KODI18_CONF_OPTS += -DWITH_ARCH=arm -DWITH_CPU=arm
else ifeq ($(BR2_mips)$(BR2_mipsel)$(BR2_mips64)$(BR2_mips64el),y)
KODI18_CONF_OPTS += \
	-DWITH_ARCH=mips$(if $(BR2_ARCH_IS_64),64) \
	-DWITH_CPU=mips$(if $(BR2_ARCH_IS_64),64)
else ifeq ($(BR2_powerpc)$(BR2_powerpc64le),y)
KODI18_CONF_OPTS += \
	-DWITH_ARCH=powerpc$(if $(BR2_ARCH_IS_64),64) \
	-DWITH_CPU=powerpc$(if $(BR2_ARCH_IS_64),64)
else ifeq ($(BR2_powerpc64)$(BR2_sparc64)$(BR2_sh4)$(BR2_xtensa),y)
KODI18_CONF_OPTS += -DWITH_ARCH=$(BR2_ARCH) -DWITH_CPU=$(BR2_ARCH)
else
# Kodi auto-detects ARCH, tested: arm, aarch64, i386, x86_64
# see project/cmake/scripts/linux/ArchSetup.cmake
KODI18_CONF_OPTS += -DWITH_CPU=$(BR2_ARCH)
endif

ifeq ($(BR2_X86_CPU_HAS_SSE),y)
KODI18_CONF_OPTS += -D_SSE_OK=ON -D_SSE_TRUE=ON
else
KODI18_CONF_OPTS += -D_SSE_OK=OFF -D_SSE_TRUE=OFF
endif

ifeq ($(BR2_X86_CPU_HAS_SSE2),y)
KODI18_CONF_OPTS += -D_SSE2_OK=ON -D_SSE2_TRUE=ON
else
KODI18_CONF_OPTS += -D_SSE2_OK=OFF -D_SSE2_TRUE=OFF
endif

ifeq ($(BR2_X86_CPU_HAS_SSE3),y)
KODI18_CONF_OPTS += -D_SSE3_OK=ON -D_SSE3_TRUE=ON
else
KODI18_CONF_OPTS += -D_SSE3_OK=OFF -D_SSE3_TRUE=OFF
endif

ifeq ($(BR2_X86_CPU_HAS_SSSE3),y)
KODI18_CONF_OPTS += -D_SSSE3_OK=ON -D_SSSE3_TRUE=ON
else
KODI18_CONF_OPTS += -D_SSSE3_OK=OFF -D_SSSE3_TRUE=OFF
endif

ifeq ($(BR2_X86_CPU_HAS_SSE4),y)
KODI18_CONF_OPTS += -D_SSE41_OK=ON -D_SSE41_TRUE=ON
else
KODI18_CONF_OPTS += -D_SSE41_OK=OFF -D_SSE41_TRUE=OFF
endif

ifeq ($(BR2_X86_CPU_HAS_SSE42),y)
KODI18_CONF_OPTS += -D_SSE42_OK=ON -D_SSE42_TRUE=ON
else
KODI18_CONF_OPTS += -D_SSE42_OK=OFF -D_SSE42_TRUE=OFF
endif

ifeq ($(BR2_X86_CPU_HAS_AVX),y)
KODI18_CONF_OPTS += -D_AVX_OK=ON -D_AVX_TRUE=ON
else
KODI18_CONF_OPTS += -D_AVX_OK=OFF -D_AVX_TRUE=OFF
endif

ifeq ($(BR2_X86_CPU_HAS_AVX2),y)
KODI18_CONF_OPTS += -D_AVX2_OK=ON -D_AVX2_TRUE=ON
else
KODI18_CONF_OPTS += -D_AVX2_OK=OFF -D_AVX2_TRUE=OFF
endif

# mips: uses __atomic_load_8
ifeq ($(BR2_TOOLCHAIN_HAS_LIBATOMIC),y)
KODI18_CXX_FLAGS += -latomic
endif

ifeq ($(BR2_PACKAGE_KODI18_PLATFORM_GBM_GL),y)
KODI18_CONF_OPTS += \
	-DCORE_PLATFORM_NAME=gbm \
	-DGBM_RENDER_SYSTEM=gl
KODI18_DEPENDENCIES += libegl libglu libinput libxkbcommon mesa3d
endif

ifeq ($(BR2_PACKAGE_KODI18_PLATFORM_GBM_GLES),y)
KODI18_CONF_OPTS += \
	-DCORE_PLATFORM_NAME=gbm \
	-DGBM_RENDER_SYSTEM=gles

KODI18_DEPENDENCIES += libgles libinput libxkbcommon
ifeq ($(BR2_PACKAGE_MESA3D),y)
	KODI18_DEPENDENCIES += mesa3d
endif
endif

ifeq ($(BR2_PACKAGE_KODI18_PLATFORM_RBPI),y)
KODI18_CONF_OPTS += -DCORE_PLATFORM_NAME=rbpi
KODI18_DEPENDENCIES += rpi-userland libinput libxkbcommon 
endif

ifeq ($(BR2_PACKAGE_KODI18_PLATFORM_WAYLAND_GL),y)
KODI18_CONF_OPTS += \
	-DCORE_PLATFORM_NAME=wayland \
	-DWAYLAND_RENDER_SYSTEM=gl
KODI18_DEPENDENCIES += libegl libgl libglu libxkbcommon waylandpp
endif

ifeq ($(BR2_PACKAGE_KODI18_PLATFORM_WAYLAND_GLES),y)
KODI18_CONF_OPTS += \
	-DCORE_PLATFORM_NAME=wayland \
	-DWAYLAND_RENDER_SYSTEM=gles
KODI18_C_FLAGS += `$(PKG_CONFIG_HOST_BINARY) --cflags egl`
KODI18_CXX_FLAGS += `$(PKG_CONFIG_HOST_BINARY) --cflags egl`
KODI18_DEPENDENCIES += libegl libgles libxkbcommon waylandpp
endif

ifeq ($(BR2_PACKAGE_KODI18_PLATFORM_X11_OPENGL),y)
KODI18_CONF_OPTS += -DCORE_PLATFORM_NAME=x11
KODI18_DEPENDENCIES += libegl libglu libgl xlib_libX11 xlib_libXext \
	xlib_libXrandr libdrm
endif

ifeq ($(BR2_PACKAGE_KODI18_MYSQL),y)
KODI18_CONF_OPTS += -DENABLE_MYSQLCLIENT=ON
KODI18_DEPENDENCIES += mysql
else
KODI18_CONF_OPTS += -DENABLE_MYSQLCLIENT=OFF
endif

ifeq ($(BR2_PACKAGE_HAS_UDEV),y)
KODI18_CONF_OPTS += -DENABLE_UDEV=ON
KODI18_DEPENDENCIES += udev
else
KODI18_CONF_OPTS += -DENABLE_UDEV=OFF
ifeq ($(BR2_PACKAGE_KODI18_LIBUSB),y)
KODI18_CONF_OPTS += -DENABLE_LIBUSB=ON
KODI18_DEPENDENCIES += libusb-compat
endif
endif

ifeq ($(BR2_PACKAGE_LIBCAP),y)
KODI18_CONF_OPTS += -DENABLE_CAP=ON
KODI18_DEPENDENCIES += libcap
else
KODI18_CONF_OPTS += -DENABLE_CAP=OFF
endif

ifeq ($(BR2_PACKAGE_LIBXML2)$(BR2_PACKAGE_LIBXSLT),yy)
KODI18_CONF_OPTS += -DENABLE_XSLT=ON
KODI18_DEPENDENCIES += libxml2 libxslt
else
KODI18_CONF_OPTS += -DENABLE_XSLT=OFF
endif

ifeq ($(BR2_PACKAGE_KODI18_BLUEZ),y)
KODI18_CONF_OPTS += -DENABLE_BLUETOOTH=ON
KODI18_DEPENDENCIES += bluez5_utils
else
KODI18_CONF_OPTS += -DENABLE_BLUETOOTH=OFF
endif

ifeq ($(BR2_PACKAGE_KODI18_DBUS),y)
KODI18_DEPENDENCIES += dbus
KODI18_CONF_OPTS += -DENABLE_DBUS=ON
else
KODI18_CONF_OPTS += -DENABLE_DBUS=OFF
endif

ifeq ($(BR2_PACKAGE_KODI18_EVENTCLIENTS),y)
KODI18_CONF_OPTS += -DENABLE_EVENTCLIENTS=ON
else
KODI18_CONF_OPTS += -DENABLE_EVENTCLIENTS=OFF
endif

ifeq ($(BR2_PACKAGE_KODI18_ALSA_LIB),y)
KODI18_CONF_OPTS += -DENABLE_ALSA=ON
KODI18_DEPENDENCIES += alsa-lib
else
KODI18_CONF_OPTS += -DENABLE_ALSA=OFF
endif

ifeq ($(BR2_PACKAGE_KODI18_LIBMICROHTTPD),y)
KODI18_CONF_OPTS += -DENABLE_MICROHTTPD=ON
KODI18_DEPENDENCIES += libmicrohttpd
else
KODI18_CONF_OPTS += -DENABLE_MICROHTTPD=OFF
endif

ifeq ($(BR2_PACKAGE_KODI18_LIBSMBCLIENT),y)
KODI18_DEPENDENCIES += samba4
KODI18_CONF_OPTS += -DENABLE_SMBCLIENT=ON
else
KODI18_CONF_OPTS += -DENABLE_SMBCLIENT=OFF
endif

ifeq ($(BR2_PACKAGE_KODI18_LIBNFS),y)
KODI18_DEPENDENCIES += libnfs
KODI18_CONF_OPTS += -DENABLE_NFS=ON
else
KODI18_CONF_OPTS += -DENABLE_NFS=OFF
endif

ifeq ($(BR2_PACKAGE_KODI18_LIBBLURAY),y)
KODI18_DEPENDENCIES += libbluray
KODI18_CONF_OPTS += -DENABLE_BLURAY=ON
else
KODI18_CONF_OPTS += -DENABLE_BLURAY=OFF
endif

ifeq ($(BR2_PACKAGE_KODI18_LIBSHAIRPLAY),y)
KODI18_DEPENDENCIES += libshairplay
KODI18_CONF_OPTS += -DENABLE_AIRTUNES=ON
else
KODI18_CONF_OPTS += -DENABLE_AIRTUNES=OFF
endif

ifeq ($(BR2_PACKAGE_KODI18_AVAHI),y)
KODI18_DEPENDENCIES += avahi
KODI18_CONF_OPTS += -DENABLE_AVAHI=ON
else
KODI18_CONF_OPTS += -DENABLE_AVAHI=OFF
endif

ifeq ($(BR2_PACKAGE_KODI18_LIBCEC),y)
KODI18_DEPENDENCIES += libcec
KODI18_CONF_OPTS += -DENABLE_CEC=ON
else
KODI18_CONF_OPTS += -DENABLE_CEC=OFF
endif

ifeq ($(BR2_PACKAGE_KODI18_LCMS2),y)
KODI18_DEPENDENCIES += lcms2
KODI18_CONF_OPTS += -DENABLE_LCMS2=ON
else
KODI18_CONF_OPTS += -DENABLE_LCMS2=OFF
endif

ifeq ($(BR2_PACKAGE_LIRC_TOOLS),y)
KODI18_DEPENDENCIES += lirc-tools
endif

ifeq ($(BR2_PACKAGE_KODI18_LIBTHEORA),y)
KODI18_DEPENDENCIES += libtheora
endif

# kodi18 needs libva & libva-glx
ifeq ($(BR2_PACKAGE_KODI18_LIBVA)$(BR2_PACKAGE_MESA3D_DRI_DRIVER),yy)
KODI18_DEPENDENCIES += mesa3d libva
KODI18_CONF_OPTS += -DENABLE_VAAPI=ON
else
KODI18_CONF_OPTS += -DENABLE_VAAPI=OFF
endif

ifeq ($(BR2_PACKAGE_KODI18_LIBVDPAU),y)
KODI18_DEPENDENCIES += libvdpau
KODI18_CONF_OPTS += -DENABLE_VDPAU=ON
else
KODI18_CONF_OPTS += -DENABLE_VDPAU=OFF
endif

ifeq ($(BR2_PACKAGE_KODI18_UPNP),y)
KODI18_CONF_OPTS += -DENABLE_UPNP=ON
else
KODI18_CONF_OPTS += -DENABLE_UPNP=OFF
endif

ifeq ($(BR2_PACKAGE_KODI18_OPTICALDRIVE),y)
KODI18_CONF_OPTS += -DENABLE_OPTICAL=ON
else
KODI18_CONF_OPTS += -DENABLE_OPTICAL=OFF
endif

ifeq ($(BR2_PACKAGE_KODI18_PULSEAUDIO),y)
KODI18_CONF_OPTS += -DENABLE_PULSEAUDIO=ON
KODI18_DEPENDENCIES += pulseaudio
else
KODI18_CONF_OPTS += -DENABLE_PULSEAUDIO=OFF
endif

# Remove versioncheck addon, updating Kodi is done by building a new
# buildroot image.
KODI18_ADDON_MANIFEST = $(TARGET_DIR)/usr/share/kodi/system/addon-manifest.xml
define KODI18_CLEAN_UNUSED_ADDONS
	rm -Rf $(TARGET_DIR)/usr/share/kodi/addons/service.xbmc.versioncheck
	$(HOST_DIR)/bin/xml ed -L \
		-d "/addons/addon[text()='service.xbmc.versioncheck']" \
		$(KODI18_ADDON_MANIFEST)
endef
KODI18_POST_INSTALL_TARGET_HOOKS += KODI18_CLEAN_UNUSED_ADDONS

# Skins estuary and estouchy are installed by default and need to be
# removed if they are disabled in buildroot
ifeq ($(BR2_PACKAGE_KODI18_SKIN_ESTUARY),y)
define KODI18_CLEAN_SKIN_ESTUARY
	find $(TARGET_DIR)/usr/share/kodi/addons/skin.estuary/media -name *.gif -delete
	find $(TARGET_DIR)/usr/share/kodi/addons/skin.estuary/media -name *.jpg -delete
	find $(TARGET_DIR)/usr/share/kodi/addons/skin.estuary/media -name *.png -delete
endef
KODI18_POST_INSTALL_TARGET_HOOKS += KODI18_CLEAN_SKIN_ESTUARY
else
define KODI18_REMOVE_SKIN_ESTUARY
	rm -Rf $(TARGET_DIR)/usr/share/kodi/addons/skin.estuary
	$(HOST_DIR)/bin/xml ed -L \
		-d "/addons/addon[text()='skin.estuary']" \
		$(KODI18_ADDON_MANIFEST)
endef
KODI18_POST_INSTALL_TARGET_HOOKS += KODI18_REMOVE_SKIN_ESTUARY
endif

ifeq ($(BR2_PACKAGE_KODI18_SKIN_ESTOUCHY),y)
define KODI18_CLEAN_SKIN_ESTOUCHY
	find $(TARGET_DIR)/usr/share/kodi/addons/skin.estouchy/media -name *.gif -delete
	find $(TARGET_DIR)/usr/share/kodi/addons/skin.estouchy/media -name *.jpg -delete
	find $(TARGET_DIR)/usr/share/kodi/addons/skin.estouchy/media -name *.png -delete
endef
KODI18_POST_INSTALL_TARGET_HOOKS += KODI18_CLEAN_SKIN_ESTOUCHY
else
define KODI18_REMOVE_SKIN_ESTOUCHY
	rm -Rf $(TARGET_DIR)/usr/share/kodi/addons/skin.estouchy
	$(HOST_DIR)/bin/xml ed -L \
		-d "/addons/addon[text()='skin.estouchy']" \
		$(KODI18_ADDON_MANIFEST)
endef
KODI18_POST_INSTALL_TARGET_HOOKS += KODI18_REMOVE_SKIN_ESTOUCHY
endif

# The default value 'skin.estuary' is stored in
# xbmc/system/settings/settings.xml.
# If skin estuary is disabled this value needs to be changed to avoid
# https://github.com/xbmc/xbmc/blob/32a6916059a0b14ab5fc65cedb17b2615c039918/xbmc/Application.cpp#L1124

define KODI18_SET_DEFAULT_SKIN_ESTOUCHY
	$(SED) 's/skin.estuary/skin.estouchy/#g' $(TARGET_DIR)/usr/share/kodi/system/settings/settings.xml
endef

define KODI18_SET_DEFAULT_SKIN_CONFLUENCE
	$(SED) 's/skin.estuary/skin.confluence/#g' $(TARGET_DIR)/usr/share/kodi/system/settings/settings.xml
	$(HOST_DIR)/bin/xml ed -L -O --subnode "/addons" \
		-t elem -n "addon" -v "skin.confluence" \
		$(KODI18_ADDON_MANIFEST)
endef

ifeq ($(BR2_PACKAGE_KODI18_SKIN_DEFAULT_ESTOUCHY),y)
KODI18_POST_INSTALL_TARGET_HOOKS += KODI18_SET_DEFAULT_SKIN_ESTOUCHY
else ifeq ($(BR2_PACKAGE_KODI18_SKIN_DEFAULT_CONFLUENCE),y)
KODI18_POST_INSTALL_TARGET_HOOKS += KODI18_SET_DEFAULT_SKIN_CONFLUENCE
endif

define KODI18_INSTALL_BR_WRAPPER
	$(INSTALL) -D -m 0755 package/kodi/br-kodi \
		$(TARGET_DIR)/usr/bin/br-kodi
endef
KODI18_POST_INSTALL_TARGET_HOOKS += KODI18_INSTALL_BR_WRAPPER

# When run from a startup script, Kodi has no $HOME where to store its
# configuration, so ends up storing it in /.kodi  (yes, at the root of
# the rootfs). This is a problem for read-only filesystems. But we can't
# easily change that, so create /.kodi as a symlink where we want the
# config to eventually be. Add synlinks for the legacy XBMC name as well
define KODI18_INSTALL_CONFIG_DIR
	$(INSTALL) -d -m 0755 $(TARGET_DIR)/var/kodi
	ln -sf /var/kodi $(TARGET_DIR)/.kodi
	ln -sf /var/kodi $(TARGET_DIR)/var/xbmc
	ln -sf /var/kodi $(TARGET_DIR)/.xbmc
endef
KODI18_POST_INSTALL_TARGET_HOOKS += KODI18_INSTALL_CONFIG_DIR

define KODI18_INSTALL_INIT_SYSV
	$(INSTALL) -D -m 755 package/kodi/S50kodi \
		$(TARGET_DIR)/etc/init.d/S50kodi
endef

define KODI18_INSTALL_INIT_SYSTEMD
	$(INSTALL) -D -m 644 package/kodi/kodi.service \
		$(TARGET_DIR)/usr/lib/systemd/system/kodi.service
endef

$(eval $(cmake-package))
