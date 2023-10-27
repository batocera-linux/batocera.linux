################################################################################
#
# kodi20
#
################################################################################

# When updating the version, please also update kodi20-jsonschemabuilder
# and kodi20-texturepacker
KODI20_VERSION_MAJOR = 20.2
KODI20_VERSION_NAME = Nexus
KODI20_VERSION = $(KODI20_VERSION_MAJOR)-$(KODI20_VERSION_NAME)
KODI20_SITE = $(call github,xbmc,xbmc,$(KODI20_VERSION))
KODI20_LICENSE = GPL-2.0
KODI20_LICENSE_FILES = LICENSE.md
KODI20_CPE_ID_VENDOR = kodi
KODI20_CPE_ID_VERSION = $(KODI20_VERSION_MAJOR)
# needed for binary addons
KODI20_INSTALL_STAGING = YES
# kodi recommends building out-of-source
KODI20_SUPPORTS_IN_SOURCE_BUILD = NO
KODI20_DEPENDENCIES = \
	ffmpeg \
	flatbuffers \
	fmt \
	fontconfig \
	freetype \
	fstrcmp \
	giflib \
	host-flatbuffers \
	host-gawk \
	host-gettext \
	host-gperf \
	host-kodi20-jsonschemabuilder \
	host-kodi20-texturepacker \
	host-nasm \
	host-swig \
	host-xmlstarlet \
	jpeg \
	libass \
	libcdio \
	libcrossguid \
	libcurl \
	libdrm \
	libegl \
	libfribidi \
	libplist \
	libpng \
	lzo \
	openssl \
	pcre \
	python3 \
	rapidjson \
	spdlog \
	sqlite \
	taglib \
	tinyxml \
	zlib

# taken from tools/depends/target/*/*-VERSION
KODI20_LIBDVDCSS_VERSION = 1.4.3-Next-Nexus-Alpha2-2
KODI20_LIBDVDNAV_VERSION = 6.1.1-Next-Nexus-Alpha2-2
KODI20_LIBDVDREAD_VERSION = 6.1.3-Next-Nexus-Alpha2-2
KODI20_EXTRA_DOWNLOADS += \
	$(call github,xbmc,libdvdcss,$(KODI20_LIBDVDCSS_VERSION))/kodi20-libdvdcss-$(KODI20_LIBDVDCSS_VERSION).tar.gz \
	$(call github,xbmc,libdvdnav,$(KODI20_LIBDVDNAV_VERSION))/kodi20-libdvdnav-$(KODI20_LIBDVDNAV_VERSION).tar.gz \
	$(call github,xbmc,libdvdread,$(KODI20_LIBDVDREAD_VERSION))/kodi20-libdvdread-$(KODI20_LIBDVDREAD_VERSION).tar.gz

KODI20_CONF_OPTS += \
    -DADDONS_CONFIGURE_AT_STARTUP=OFF \
	-DCMAKE_C_FLAGS="$(TARGET_CFLAGS) $(KODI20_C_FLAGS)" \
	-DENABLE_APP_AUTONAME=OFF \
	-DENABLE_CCACHE=OFF \
	-DENABLE_DVDCSS=ON \
	-DENABLE_INTERNAL_CROSSGUID=OFF \
	-DWITH_FFMPEG=$(STAGING_DIR)/usr \
	-DENABLE_INTERNAL_FLATBUFFERS=OFF \
	-DFLATBUFFERS_FLATC_EXECUTABLE=$(HOST_DIR)/bin/flatc \
	-DENABLE_INTERNAL_RapidJSON=OFF \
	-DENABLE_INTERNAL_SPDLOG=OFF \
	-DKODI_DEPENDSBUILD=OFF \
	-DENABLE_GOLD=OFF \
	-DCLANG_FORMAT_EXECUTABLE=OFF \
	-DHOST_CAN_EXECUTE_TARGET=FALSE \
	-DNATIVEPREFIX=$(HOST_DIR) \
	-DDEPENDS_PATH=$(STAGING_DIR)/usr \
	-DENABLE_TESTING=OFF \
	-DPYTHON_EXECUTABLE=$(HOST_DIR)/bin/python \
	-DPYTHON_INCLUDE_DIRS=$(STAGING_DIR)/usr/include/python$(PYTHON3_VERSION_MAJOR) \
	-DPYTHON_PATH=$(STAGING_DIR)/usr/lib/python$(PYTHON3_VERSION_MAJOR) \
	-DPYTHON_VER=$(PYTHON3_VERSION_MAJOR) \
	-DWITH_JSONSCHEMABUILDER=$(HOST_DIR)/bin/JsonSchemaBuilder \
	-DWITH_TEXTUREPACKER=$(HOST_DIR)/bin/TexturePacker \
	-DLIBDVDCSS_URL=$(KODI20_DL_DIR)/kodi20-libdvdcss-$(KODI20_LIBDVDCSS_VERSION).tar.gz \
	-DLIBDVDNAV_URL=$(KODI20_DL_DIR)/kodi20-libdvdnav-$(KODI20_LIBDVDNAV_VERSION).tar.gz \
	-DLIBDVDREAD_URL=$(KODI20_DL_DIR)/kodi20-libdvdread-$(KODI20_LIBDVDREAD_VERSION).tar.gz

ifeq ($(BR2_PACKAGE_KODI20_RENDER_SYSTEM_GL),y)
KODI20_CONF_OPTS += -DAPP_RENDER_SYSTEM=gl
KODI20_DEPENDENCIES += libgl libglu
else ifeq ($(BR2_PACKAGE_KODI20_RENDER_SYSTEM_GLES),y)
KODI20_CONF_OPTS += -DAPP_RENDER_SYSTEM=gles
KODI20_DEPENDENCIES += libgles
endif

ifeq ($(BR2_PACKAGE_KODI20_PLATFORM_SUPPORTS_GBM),y)
KODI20_CORE_PLATFORM_NAME += gbm
KODI20_DEPENDENCIES += libinput libxkbcommon # libgbm  removed, batocera

#batocera
ifeq ($(BR2_PACKAGE_HAS_LIBGBM),y)
  KODI20_DEPENDENCIES += libgbm
endif

# batocera - for mali boards
ifeq ($(BR2_PACKAGE_HAS_LIBMALI),y)
KODI20_DEPENDENCIES += libmali
endif
endif

ifeq ($(BR2_PACKAGE_KODI20_PLATFORM_SUPPORTS_WAYLAND),y)
KODI20_CONF_OPTS += \
	-DPC_WAYLANDPP_SCANNER=$(HOST_DIR)/bin/wayland-scanner \
	-DPC_WAYLANDPP_SCANNER_FOUND=ON
KODI20_CORE_PLATFORM_NAME += wayland
KODI20_DEPENDENCIES += libxkbcommon waylandpp
endif

ifeq ($(BR2_PACKAGE_KODI20_PLATFORM_SUPPORTS_X11),y)
KODI20_CORE_PLATFORM_NAME += x11
KODI20_DEPENDENCIES += \
	xlib_libX11 \
	xlib_libXext \
	xlib_libXrandr
endif

KODI20_CONF_OPTS += -DCORE_PLATFORM_NAME="$(KODI20_CORE_PLATFORM_NAME)"

ifeq ($(BR2_ENABLE_LOCALE),)
KODI20_DEPENDENCIES += libiconv
endif

ifeq ($(BR2_arceb)$(BR2_arcle),y)
KODI20_CONF_OPTS += -DWITH_ARCH=arc -DWITH_CPU=arc
else ifeq ($(BR2_armeb),y)
KODI20_CONF_OPTS += -DWITH_ARCH=arm -DWITH_CPU=arm
else ifeq ($(BR2_mips)$(BR2_mipsel)$(BR2_mips64)$(BR2_mips64el),y)
KODI20_CONF_OPTS += \
	-DWITH_ARCH=mips$(if $(BR2_ARCH_IS_64),64) \
	-DWITH_CPU=mips$(if $(BR2_ARCH_IS_64),64)
else ifeq ($(BR2_powerpc)$(BR2_powerpc64le),y)
KODI20_CONF_OPTS += \
	-DWITH_ARCH=powerpc$(if $(BR2_ARCH_IS_64),64) \
	-DWITH_CPU=powerpc$(if $(BR2_ARCH_IS_64),64)
else ifeq ($(BR2_or1k)$(BR2_powerpc64)$(BR2_riscv)$(BR2_sparc64)$(BR2_sh4)$(BR2_xtensa),y)
KODI20_CONF_OPTS += -DWITH_ARCH=$(BR2_ARCH) -DWITH_CPU=$(BR2_ARCH)
else
# Kodi auto-detects ARCH, tested: arm, aarch64, i386, x86_64
# see project/cmake/scripts/linux/ArchSetup.cmake
KODI20_CONF_OPTS += -DWITH_CPU=$(BR2_ARCH)
endif

ifeq ($(BR2_ARM_CPU_HAS_NEON),y)
KODI20_CONF_OPTS += -DENABLE_NEON=ON
else ifeq ($(BR2_aarch64),y)
KODI20_CONF_OPTS += -DENABLE_NEON=ON
else
KODI20_CONF_OPTS += -DENABLE_NEON=OFF
endif

ifeq ($(BR2_X86_CPU_HAS_SSE),y)
KODI20_CONF_OPTS += -D_SSE_OK=ON -D_SSE_TRUE=ON
else
KODI20_CONF_OPTS += -D_SSE_OK=OFF -D_SSE_TRUE=OFF
endif

ifeq ($(BR2_X86_CPU_HAS_SSE2),y)
KODI20_CONF_OPTS += -D_SSE2_OK=ON -D_SSE2_TRUE=ON
else
KODI20_CONF_OPTS += -D_SSE2_OK=OFF -D_SSE2_TRUE=OFF
endif

ifeq ($(BR2_X86_CPU_HAS_SSE3),y)
KODI20_CONF_OPTS += -D_SSE3_OK=ON -D_SSE3_TRUE=ON
else
KODI20_CONF_OPTS += -D_SSE3_OK=OFF -D_SSE3_TRUE=OFF
endif

ifeq ($(BR2_X86_CPU_HAS_SSSE3),y)
KODI20_CONF_OPTS += -D_SSSE3_OK=ON -D_SSSE3_TRUE=ON
else
KODI20_CONF_OPTS += -D_SSSE3_OK=OFF -D_SSSE3_TRUE=OFF
endif

ifeq ($(BR2_X86_CPU_HAS_SSE4),y)
KODI20_CONF_OPTS += -D_SSE41_OK=ON -D_SSE41_TRUE=ON
else
KODI20_CONF_OPTS += -D_SSE41_OK=OFF -D_SSE41_TRUE=OFF
endif

ifeq ($(BR2_X86_CPU_HAS_SSE42),y)
KODI20_CONF_OPTS += -D_SSE42_OK=ON -D_SSE42_TRUE=ON
else
KODI20_CONF_OPTS += -D_SSE42_OK=OFF -D_SSE42_TRUE=OFF
endif

ifeq ($(BR2_X86_CPU_HAS_AVX),y)
KODI20_CONF_OPTS += -D_AVX_OK=ON -D_AVX_TRUE=ON
else
KODI20_CONF_OPTS += -D_AVX_OK=OFF -D_AVX_TRUE=OFF
endif

ifeq ($(BR2_X86_CPU_HAS_AVX2),y)
KODI20_CONF_OPTS += -D_AVX2_OK=ON -D_AVX2_TRUE=ON
else
KODI20_CONF_OPTS += -D_AVX2_OK=OFF -D_AVX2_TRUE=OFF
endif

# mips: uses __atomic_load_8
ifeq ($(BR2_TOOLCHAIN_HAS_LIBATOMIC),y)
KODI20_CONF_OPTS += -DCMAKE_EXE_LINKER_FLAGS=-latomic
endif

ifeq ($(BR2_PACKAGE_KODI20_PLATFORM_GBM_GLES),y)
KODI20_CONF_OPTS += \
        -DCORE_PLATFORM_NAME=gbm \
        -DGBM_RENDER_SYSTEM=gles
KODI20_DEPENDENCIES += libgles libinput libxkbcommon
ifeq ($(BR2_PACKAGE_PROVIDES_LIBGLES),mesa3d)
        KODI20_DEPENDENCIES += mesa3d
endif
endif

ifeq ($(BR2_TOOLCHAIN_GCC_AT_LEAST_5),)
KODI20_C_FLAGS += -std=gnu99
endif

ifeq ($(BR2_PACKAGE_KODI20_MYSQL),y)
KODI20_CONF_OPTS += -DENABLE_MYSQLCLIENT=ON
KODI20_DEPENDENCIES += mysql
else
KODI20_CONF_OPTS += -DENABLE_MYSQLCLIENT=OFF
endif

ifeq ($(BR2_PACKAGE_HAS_UDEV),y)
KODI20_CONF_OPTS += -DENABLE_UDEV=ON
KODI20_DEPENDENCIES += udev
else
KODI20_CONF_OPTS += -DENABLE_UDEV=OFF
ifeq ($(BR2_PACKAGE_KODI20_LIBUSB),y)
KODI20_CONF_OPTS += -DENABLE_LIBUSB=ON
KODI20_DEPENDENCIES += libusb-compat
else
KODI20_CONF_OPTS += -DENABLE_LIBUSB=OFF
endif
endif

ifeq ($(BR2_PACKAGE_LIBCAP),y)
KODI20_CONF_OPTS += -DENABLE_CAP=ON
KODI20_DEPENDENCIES += libcap
else
KODI20_CONF_OPTS += -DENABLE_CAP=OFF
endif

ifeq ($(BR2_PACKAGE_LIBXML2)$(BR2_PACKAGE_LIBXSLT),yy)
KODI20_CONF_OPTS += -DENABLE_XSLT=ON
KODI20_DEPENDENCIES += libxml2 libxslt
else
KODI20_CONF_OPTS += -DENABLE_XSLT=OFF
endif

ifeq ($(BR2_PACKAGE_KODI20_BLUEZ),y)
KODI20_CONF_OPTS += -DENABLE_BLUETOOTH=ON
KODI20_DEPENDENCIES += bluez5_utils
else
KODI20_CONF_OPTS += -DENABLE_BLUETOOTH=OFF
endif

ifeq ($(BR2_PACKAGE_KODI20_DBUS),y)
KODI20_DEPENDENCIES += dbus
KODI20_CONF_OPTS += -DENABLE_DBUS=ON
else
KODI20_CONF_OPTS += -DENABLE_DBUS=OFF
endif

ifeq ($(BR2_PACKAGE_KODI20_EVENTCLIENTS),y)
KODI20_CONF_OPTS += -DENABLE_EVENTCLIENTS=ON
else
KODI20_CONF_OPTS += -DENABLE_EVENTCLIENTS=OFF
endif

# batocera
ifeq ($(BR2_PACKAGE_KODI20_GBM),y)
  ifeq ($(BR2_PACKAGE_MESA3D),y)
    KODI20_DEPENDENCIES += mesa3d
  endif
KODI20_CONF_OPTS += -DENABLE_GBM=ON
else
KODI20_CONF_OPTS += -DENABLE_GBM=OFF
endif

ifeq ($(BR2_PACKAGE_KODI20_ALSA_LIB),y)
KODI20_CONF_OPTS += -DENABLE_ALSA=ON
KODI20_DEPENDENCIES += alsa-lib
# disable pipewire too
KODI20_CONF_OPTS += -DENABLE_PIPEWIRE=OFF
else
KODI20_CONF_OPTS += -DENABLE_ALSA=OFF
endif

ifeq ($(BR2_PACKAGE_KODI20_LIBMICROHTTPD),y)
KODI20_CONF_OPTS += -DENABLE_MICROHTTPD=ON
KODI20_DEPENDENCIES += libmicrohttpd
else
KODI20_CONF_OPTS += -DENABLE_MICROHTTPD=OFF
endif

ifeq ($(BR2_PACKAGE_KODI20_LIBSMBCLIENT),y)
KODI20_DEPENDENCIES += samba4
KODI20_CONF_OPTS += -DENABLE_SMBCLIENT=ON
else
KODI20_CONF_OPTS += -DENABLE_SMBCLIENT=OFF
endif

ifeq ($(BR2_PACKAGE_KODI20_LIBNFS),y)
KODI20_DEPENDENCIES += libnfs
KODI20_CONF_OPTS += -DENABLE_NFS=ON
else
KODI20_CONF_OPTS += -DENABLE_NFS=OFF
endif

ifeq ($(BR2_PACKAGE_KODI20_LIBBLURAY),y)
KODI20_DEPENDENCIES += libbluray
KODI20_CONF_OPTS += -DENABLE_BLURAY=ON
else
KODI20_CONF_OPTS += -DENABLE_BLURAY=OFF
endif

ifeq ($(BR2_PACKAGE_KODI20_LIBSHAIRPLAY),y)
KODI20_DEPENDENCIES += libshairplay
KODI20_CONF_OPTS += -DENABLE_AIRTUNES=ON
else
KODI20_CONF_OPTS += -DENABLE_AIRTUNES=OFF
endif

ifeq ($(BR2_PACKAGE_KODI20_AVAHI),y)
KODI20_DEPENDENCIES += avahi
KODI20_CONF_OPTS += -DENABLE_AVAHI=ON
else
KODI20_CONF_OPTS += -DENABLE_AVAHI=OFF
endif

ifeq ($(BR2_PACKAGE_KODI20_LIBCEC),y)
KODI20_DEPENDENCIES += libcec
KODI20_CONF_OPTS += -DENABLE_CEC=ON
else
KODI20_CONF_OPTS += -DENABLE_CEC=OFF
endif

ifeq ($(BR2_PACKAGE_KODI20_LCMS2),y)
KODI20_DEPENDENCIES += lcms2
KODI20_CONF_OPTS += -DENABLE_LCMS2=ON
else
KODI20_CONF_OPTS += -DENABLE_LCMS2=OFF
endif

ifeq ($(BR2_PACKAGE_LIRC_TOOLS),y)
KODI20_DEPENDENCIES += lirc-tools
endif

ifeq ($(BR2_PACKAGE_LIBVA),y)
KODI20_DEPENDENCIES += libva
KODI20_CONF_OPTS += -DENABLE_VAAPI=ON
else
KODI20_CONF_OPTS += -DENABLE_VAAPI=OFF
endif

ifeq ($(BR2_PACKAGE_KODI20_LIBVDPAU),y)
KODI20_DEPENDENCIES += libvdpau
KODI20_CONF_OPTS += -DENABLE_VDPAU=ON
else
KODI20_CONF_OPTS += -DENABLE_VDPAU=OFF
endif

ifeq ($(BR2_PACKAGE_KODI20_UPNP),y)
KODI20_CONF_OPTS += -DENABLE_UPNP=ON
else
KODI20_CONF_OPTS += -DENABLE_UPNP=OFF
endif

ifeq ($(BR2_PACKAGE_KODI20_OPTICALDRIVE),y)
KODI20_CONF_OPTS += -DENABLE_OPTICAL=ON
else
KODI20_CONF_OPTS += -DENABLE_OPTICAL=OFF
endif

# best audio support is with alsa, so disabling others for now
#ifeq ($(BR2_PACKAGE_KODI20_PULSEAUDIO),y)
#KODI20_CONF_OPTS += -DENABLE_PULSEAUDIO=ON
#KODI20_DEPENDENCIES += pulseaudio
#else
KODI20_CONF_OPTS += -DENABLE_PULSEAUDIO=OFF
#endif

ifeq ($(BR2_PACKAGE_LIBUDFREAD),y)
KODI20_DEPENDENCIES += libudfread
else
KODI20_CONF_OPTS += -DENABLE_INTERNAL_UDFREAD=OFF
endif

# Remove versioncheck addon, updating Kodi is done by building a new
# buildroot image.
KODI20_ADDON_MANIFEST = $(TARGET_DIR)/usr/share/kodi/system/addon-manifest.xml
define KODI20_CLEAN_UNUSED_ADDONS
	rm -Rf $(TARGET_DIR)/usr/share/kodi/addons/service.xbmc.versioncheck
	$(HOST_DIR)/bin/xml ed -L \
		-d "/addons/addon[text()='service.xbmc.versioncheck']" \
		$(KODI20_ADDON_MANIFEST)
endef
KODI20_POST_INSTALL_TARGET_HOOKS += KODI20_CLEAN_UNUSED_ADDONS

# When run from a startup script, Kodi has no $HOME where to store its
# configuration, so ends up storing it in /.kodi  (yes, at the root of
# the rootfs). This is a problem for read-only filesystems. But we can't
# easily change that, so create /.kodi as a symlink where we want the
# config to eventually be. Add synlinks for the legacy XBMC name as well
define KODI20_INSTALL_CONFIG_DIR
	$(INSTALL) -d -m 0755 $(TARGET_DIR)/var/kodi
	ln -sf /var/kodi $(TARGET_DIR)/.kodi
	ln -sf /var/kodi $(TARGET_DIR)/var/xbmc
	ln -sf /var/kodi $(TARGET_DIR)/.xbmc
endef
KODI20_POST_INSTALL_TARGET_HOOKS += KODI20_INSTALL_CONFIG_DIR

$(eval $(cmake-package))
