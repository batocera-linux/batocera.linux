################################################################################
#
# wine-tkg
#
################################################################################

WINE_TKG_VERSION = 10.10
WINE_TKG_SITE = https://github.com/Kron4ek/wine-tkg
WINE_TKG_SITE_METHOD = git
WINE_TKG_LICENSE = LGPL-2.1+
WINE_TKG_LICENSE_FILES = COPYING.LIB LICENSE
WINE_TKG_SELINUX_MODULES = wine
WINE_TKG_DEPENDENCIES = host-bison host-flex host-wine-tkg
HOST_WINE_TKG_DEPENDENCIES = host-bison host-flex

WINE_TKG_GIT_SUBMODULES = YES

# Wine needs its own directory structure and tools for cross compiling
WINE_TKG_CONF_OPTS = \
	--with-wine-tools=../host-wine-tkg-$(WINE_TKG_VERSION)/ \
	--disable-tests \
	--disable-win16 \
	--without-capi \
	--without-coreaudio \
	--without-gettext \
	--without-gettextpo \
	--without-gphoto \
	--without-mingw \
	--without-opencl \
	--without-oss \
	--without-ldap \
    --prefix=/usr/wine/wine-tkg \
    --exec-prefix=/usr/wine/wine-tkg

ifeq ($(BR2_x86_64),y)
WINE_TKG_CONF_OPTS += --enable-win64
WINE_TKG_DEPENDENCIES += wine-x86
else
WINE_TKG_CONF_OPTS += --disable-win64
endif

# Wine uses a wrapper around gcc, and uses the value of -host-wine--host to
# construct the filename of the gcc to call.  But for external
# toolchains, the GNU_TARGET_NAME tuple that we construct from our
# internal variables may differ from the actual gcc prefix for the
# external toolchains. So, we have to override whatever the gcc
# wrapper believes what the real gcc is named, and force the tuple of
# the external toolchain, not the one we compute in GNU_TARGET_NAME.
ifeq ($(BR2_TOOLCHAIN_EXTERNAL),y)
WINE_TKG_CONF_OPTS += TARGETFLAGS="-b $(TOOLCHAIN_EXTERNAL_PREFIX)"
endif

ifeq ($(BR2_PACKAGE_ALSA_LIB),y)
WINE_TKG_CONF_OPTS += --with-alsa
WINE_TKG_DEPENDENCIES += alsa-lib
else
WINE_TKG_CONF_OPTS += --without-alsa
endif

ifeq ($(BR2_PACKAGE_CUPS),y)
WINE_TKG_CONF_OPTS += --with-cups
WINE_TKG_DEPENDENCIES += cups
WINE_TKG_CONF_ENV += CUPS_CONFIG=$(STAGING_DIR)/usr/bin/cups-config
else
WINE_TKG_CONF_OPTS += --without-cups
endif

ifeq ($(BR2_PACKAGE_DBUS),y)
WINE_TKG_CONF_OPTS += --with-dbus
WINE_TKG_DEPENDENCIES += dbus
else
WINE_TKG_CONF_OPTS += --without-dbus
endif

ifeq ($(BR2_PACKAGE_FFMPEG),y)
WINE_TKG_CONF_OPTS += --with-ffmpeg
WINE_TKG_DEPENDENCIES += ffmpeg
else
WINE_TKG_CONF_OPTS += --without-ffmpeg
endif

ifeq ($(BR2_PACKAGE_FONTCONFIG),y)
WINE_TKG_CONF_OPTS += --with-fontconfig
WINE_TKG_DEPENDENCIES += fontconfig
else
WINE_TKG_CONF_OPTS += --without-fontconfig
endif

# To support freetype in wine we also need freetype in host-wine for the cross compiling tools
ifeq ($(BR2_PACKAGE_FREETYPE),y)
WINE_TKG_CONF_OPTS += --with-freetype
HOST_WINE_TKG_CONF_OPTS += --with-freetype
WINE_TKG_DEPENDENCIES += freetype
HOST_WINE_TKG_DEPENDENCIES += host-freetype
WINE_TKG_CONF_ENV += FREETYPE_CONFIG=$(STAGING_DIR)/usr/bin/freetype-config
else
WINE_TKG_CONF_OPTS += --without-freetype
HOST_WINE_TKG_CONF_OPTS += --without-freetype
endif

ifeq ($(BR2_PACKAGE_GNUTLS),y)
WINE_TKG_CONF_OPTS += --with-gnutls
WINE_TKG_DEPENDENCIES += gnutls
else
WINE_TKG_CONF_OPTS += --without-gnutls
endif

ifeq ($(BR2_PACKAGE_GST1_PLUGINS_BASE),y)
WINE_TKG_CONF_OPTS += --with-gstreamer
WINE_TKG_DEPENDENCIES += gst1-plugins-base
else
WINE_TKG_CONF_OPTS += --without-gstreamer
endif

ifeq ($(BR2_PACKAGE_LIBGCRYPT),y)
WINE_TKG_CONF_OPTS += --with-gcrypt
WINE_TKG_DEPENDENCIES += libgcrypt
else
WINE_TKG_CONF_OPTS += --without-gcrypt
endif

ifeq ($(BR2_PACKAGE_HAS_LIBGL),y)
WINE_TKG_CONF_OPTS += --with-opengl
WINE_TKG_DEPENDENCIES += libgl
else
WINE_TKG_CONF_OPTS += --without-opengl
endif

ifeq ($(BR2_PACKAGE_LIBKRB5),y)
WINE_TKG_CONF_OPTS += --with-krb5
WINE_TKG_DEPENDENCIES += libkrb5
else
WINE_TKG_CONF_OPTS += --without-krb5
endif

ifeq ($(BR2_PACKAGE_LIBPCAP),y)
WINE_TKG_CONF_OPTS += --with-pcap
WINE_TKG_DEPENDENCIES += libpcap
else
WINE_TKG_CONF_OPTS += --without-pcap
endif

ifeq ($(BR2_PACKAGE_LIBUSB),y)
WINE_TKG_CONF_OPTS += --with-usb
WINE_TKG_DEPENDENCIES += libusb
else
WINE_TKG_CONF_OPTS += --without-usb
endif

ifeq ($(BR2_PACKAGE_LIBV4L),y)
WINE_TKG_CONF_OPTS += --with-v4l2
WINE_TKG_DEPENDENCIES += libv4l
else
WINE_TKG_CONF_OPTS += --without-v4l2
endif

ifeq ($(BR2_PACKAGE_PCSC_LITE),y)
WINE_TKG_CONF_OPTS += --with-pcsclite
WINE_TKG_DEPENDENCIES += pcsc-lite
else
WINE_TKG_CONF_OPTS += --without-pcsclite
endif

ifeq ($(BR2_PACKAGE_PULSEAUDIO),y)
WINE_TKG_CONF_OPTS += --with-pulse
WINE_TKG_DEPENDENCIES += pulseaudio
else
WINE_TKG_CONF_OPTS += --without-pulse
endif

ifeq ($(BR2_PACKAGE_SAMBA4),y)
WINE_TKG_CONF_OPTS += --with-netapi
WINE_TKG_DEPENDENCIES += samba4
else
WINE_TKG_CONF_OPTS += --without-netapi
endif

ifeq ($(BR2_PACKAGE_SANE_BACKENDS),y)
WINE_TKG_CONF_OPTS += --with-sane
WINE_TKG_DEPENDENCIES += sane-backends
WINE_TKG_CONF_ENV += SANE_CONFIG=$(STAGING_DIR)/usr/bin/sane-config
else
WINE_TKG_CONF_OPTS += --without-sane
endif

ifeq ($(BR2_PACKAGE_SDL2),y)
WINE_TKG_CONF_OPTS += --with-sdl
WINE_TKG_DEPENDENCIES += sdl2
else
WINE_TKG_CONF_OPTS += --without-sdl
endif

ifeq ($(BR2_PACKAGE_HAS_UDEV),y)
WINE_TKG_CONF_OPTS += --with-udev
WINE_TKG_DEPENDENCIES += udev
else
WINE_TKG_CONF_OPTS += --without-udev
endif

ifeq ($(BR2_PACKAGE_VULKAN_HEADERS)$(BR2_PACKAGE_VULKAN_LOADER),yy)
WINE_TKG_CONF_OPTS += --with-vulkan
WINE_TKG_DEPENDENCIES += vulkan-headers vulkan-loader
else
WINE_TKG_CONF_OPTS += --without-vulkan
endif

ifeq ($(BR2_PACKAGE_WAYLAND),y)
WINE_TKG_CONF_OPTS += --with-wayland
WINE_TKG_DEPENDENCIES += wayland wayland-protocols libxkbcommon 
else
WINE_TKG_CONF_OPTS += --without-wayland
endif

ifeq ($(BR2_PACKAGE_XLIB_LIBX11),y)
WINE_TKG_CONF_OPTS += --with-x
WINE_TKG_DEPENDENCIES += xlib_libX11
else
WINE_TKG_CONF_OPTS += --without-x
endif

ifeq ($(BR2_PACKAGE_XLIB_LIBXCOMPOSITE),y)
WINE_TKG_CONF_OPTS += --with-xcomposite
WINE_TKG_DEPENDENCIES += xlib_libXcomposite
else
WINE_TKG_CONF_OPTS += --without-xcomposite
endif

ifeq ($(BR2_PACKAGE_XLIB_LIBXCURSOR),y)
WINE_TKG_CONF_OPTS += --with-xcursor
WINE_TKG_DEPENDENCIES += xlib_libXcursor
else
WINE_TKG_CONF_OPTS += --without-xcursor
endif

ifeq ($(BR2_PACKAGE_XLIB_LIBXEXT),y)
WINE_TKG_CONF_OPTS += --with-xshape --with-xshm
WINE_TKG_DEPENDENCIES += xlib_libXext
else
WINE_TKG_CONF_OPTS += --without-xshape --without-xshm
endif

ifeq ($(BR2_PACKAGE_XLIB_LIBXFIXES),y)
WINE_TKG_CONF_OPTS += --with-xfixes
WINE_TKG_DEPENDENCIES += xlib_libXfixes
else
WINE_TKG_CONF_OPTS += --without-xfixes
endif

ifeq ($(BR2_PACKAGE_XLIB_LIBXI),y)
WINE_TKG_CONF_OPTS += --with-xinput --with-xinput2
WINE_TKG_DEPENDENCIES += xlib_libXi
else
WINE_TKG_CONF_OPTS += --without-xinput --without-xinput2
endif

ifeq ($(BR2_PACKAGE_XLIB_LIBXINERAMA),y)
WINE_TKG_CONF_OPTS += --with-xinerama
WINE_TKG_DEPENDENCIES += xlib_libXinerama
else
WINE_TKG_CONF_OPTS += --without-xinerama
endif

ifeq ($(BR2_PACKAGE_XLIB_LIBXRANDR),y)
WINE_TKG_CONF_OPTS += --with-xrandr
WINE_TKG_DEPENDENCIES += xlib_libXrandr
else
WINE_TKG_CONF_OPTS += --without-xrandr
endif

ifeq ($(BR2_PACKAGE_XLIB_LIBXRENDER),y)
WINE_TKG_CONF_OPTS += --with-xrender
WINE_TKG_DEPENDENCIES += xlib_libXrender
else
WINE_TKG_CONF_OPTS += --without-xrender
endif

ifeq ($(BR2_PACKAGE_XLIB_LIBXXF86VM),y)
WINE_TKG_CONF_OPTS += --with-xxf86vm
WINE_TKG_DEPENDENCIES += xlib_libXxf86vm
else
WINE_TKG_CONF_OPTS += --without-xxf86vm
endif

# host-gettext is essential for .po file support in host-wine wrc
ifeq ($(BR2_SYSTEM_ENABLE_NLS),y)
HOST_WINE_TKG_DEPENDENCIES += host-gettext
HOST_WINE_TKG_CONF_OPTS += --with-gettext --with-gettextpo
else
HOST_WINE_TKG_CONF_OPTS += --without-gettext --without-gettextpo
endif

# Wine needs to enable 64-bit build tools on 64-bit host
ifneq ($(filter $(HOSTARCH),x86_64 aarch64),)
HOST_WINE_TKG_CONF_OPTS += --enable-win64
endif

ifeq ($(HOSTARCH),aarch64)
# Even though we only compile the tools, the configure script still checks if it
# can compile wine and needs help to find the right tools on aarch64
HOST_WINE_TKG_CONF_OPTS += --enable-archs=x86_64 --host=aarch64-linux-gnu
endif

# Wine only needs the host tools to be built, so cut-down the
# build time by building just what we need.
define HOST_WINE_TKG_BUILD_CMDS
	$(HOST_MAKE_ENV) $(MAKE) -C $(@D)/ __tooldeps__
endef

# Wine only needs its host variant to be built, not that it is
# installed, as it uses the tools from the build directory. But
# we have no way in Buildroot to state that a host package should
# not be installed. So, just provide an noop install command.
define HOST_WINE_TKG_INSTALL_CMDS
	:
endef

# We are focused on the cross compiling tools, disable everything else
HOST_WINE_TKG_CONF_OPTS += \
	--disable-tests \
	--disable-win16 \
	--without-alsa \
	--without-capi \
	--without-coreaudio \
	--without-cups \
	--without-dbus \
	--without-fontconfig \
	--without-gphoto \
	--without-gnutls \
	--without-gssapi \
	--without-gstreamer \
	--without-krb5 \
	--without-mingw \
	--without-netapi \
	--without-opencl \
	--without-opengl \
	--without-osmesa \
	--without-oss \
	--without-pcap \
	--without-pulse \
	--without-sane \
	--without-sdl \
	--without-usb \
	--without-v4l2 \
	--without-vulkan \
	--without-x \
	--without-xcomposite \
	--without-xcursor \
	--without-xinerama \
	--without-xinput \
	--without-xinput2 \
	--without-xrandr \
	--without-xrender \
	--without-xshape \
	--without-xshm \
	--without-xxf86vm

# Cleanup final directory
define WINE_TKG_POST_INSTALL
	mkdir -p $(TARGET_DIR)/share/wine/
	cp -pr $(@D)/nls $(TARGET_DIR)/share/wine/
    rm -Rf $(TARGET_DIR)/usr/wine/wine-tkg/include
	rm -f $(TARGET_DIR)/usr/wine/wine-tkg/lib/wine/i386-unix/*.a
endef

define WINE_TKG_64_POST_INSTALL
	mkdir -p $(TARGET_DIR)/usr/wine/wine-tkg/bin
	cp $(@D)/loader/wine64 $(TARGET_DIR)/usr/wine/wine-tkg/bin/wine
	rm -f $(TARGET_DIR)/usr/wine/wine-tkg/lib/wine/x86_64-unix/*.a
endef

WINE_TKG_POST_INSTALL_TARGET_HOOKS += WINE_TKG_POST_INSTALL

ifeq ($(BR2_x86_64),y)
WINE_TKG_POST_INSTALL_TARGET_HOOKS += WINE_TKG_64_POST_INSTALL
endif

$(eval $(autotools-package))
$(eval $(host-autotools-package))
