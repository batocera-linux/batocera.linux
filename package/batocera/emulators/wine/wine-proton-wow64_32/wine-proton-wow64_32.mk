################################################################################
#
# wine-proton-wow64_32
#
################################################################################

WINE_PROTON_WOW64_32_VERSION = proton-wine-5.13-6
WINE_PROTON_WOW64_32_SITE = $(call github,ValveSoftware,wine,$(WINE_PROTON_WOW64_32_VERSION))
WINE_PROTON_WOW64_32_LICENSE = LGPL-2.1+
WINE_PROTON_WOW64_32_DEPENDENCIES = host-bison host-flex host-wine-proton
HOST_WINE_PROTON_WOW64_32_DEPENDENCIES = host-bison host-flex

# That create folder for install
define WINE_PROTON_CREATE_WINE_FOLDER
	mkdir -p $(TARGET_DIR)/usr/wine/proton
endef

WINE_PROTON_PRE_CONFIGURE_HOOKS += WINE_PROTON_CREATE_WINE_FOLDER

# Wine needs its own directory structure and tools for cross compiling
WINE_PROTON_WOW64_32_CONF_OPTS = \
	--with-wine-tools=../host-wine-proton-$(WINE_PROTON_WOW64_32_VERSION) \
	--disable-tests \
	--without-capi \
	--without-coreaudio \
	--without-gettext \
	--without-gettextpo \
	--without-gphoto \
	--without-gsm \
	--without-hal \
	--without-opencl \
	--without-oss \
	--prefix=/usr/wine/proton \
	--exec-prefix=/usr/wine/proton

	# breaks build ??
	# --with-wine64=/build/output/images/wow64_32_part64/

# batocera
# gcrypt
ifeq ($(BR2_PACKAGE_LIBGCRYPT),y)
WINE_PROTON_WOW64_32_CONF_OPTS += --with-gcrypt
WINE_PROTON_WOW64_32_DEPENDENCIES += libgcrypt
else
WINE_PROTON_WOW64_32_CONF_OPTS += --without-gcrypt
endif

# Add FAudio if available
ifeq ($(BR2_PACKAGE_FAUDIO),y)
WINE_PROTON_WOW64_32_CONF_OPTS += --with-faudio
WINE_PROTON_WOW64_32_DEPENDENCIES += faudio
else
WINE_PROTON_WOW64_32_CONF_OPTS += --without-faudio
endif
# Add Vulkan if available
ifeq ($(BR2_PACKAGE_VULKAN_HEADERS)$(BR2_PACKAGE_VULKAN_LOADER),yy)
WINE_PROTON_WOW64_32_CONF_OPTS += --with-vulkan
WINE_PROTON_WOW64_32_DEPENDENCIES += vulkan-headers vulkan-loader
else
WINE_PROTON_WOW64_32_CONF_OPTS += --without-vulkan
endif
# Add VKD3D if available
ifeq ($(BR2_PACKAGE_VKD3D)$(BR2_PACKAGE_VULKAN_HEADERS)$(BR2_PACKAGE_VULKAN_LOADER),yyy)
WINE_PROTON_WOW64_32_CONF_OPTS += --with-vkd3d
WINE_PROTON_WOW64_32_DEPENDENCIES += vkd3d
else
WINE_PROTON_WOW64_32_CONF_OPTS += --without-vkd3d
endif
# TODO Add DXVK if available

# Wine uses a wrapper around gcc, and uses the value of --host to
# construct the filename of the gcc to call.  But for external
# toolchains, the GNU_TARGET_NAME tuple that we construct from our
# internal variables may differ from the actual gcc prefix for the
# external toolchains. So, we have to override whatever the gcc
# wrapper believes what the real gcc is named, and force the tuple of
# the external toolchain, not the one we compute in GNU_TARGET_NAME.
ifeq ($(BR2_TOOLCHAIN_EXTERNAL),y)
WINE_PROTON_WOW64_32_CONF_OPTS += TARGETFLAGS="-b $(TOOLCHAIN_EXTERNAL_PREFIX)"
endif

ifeq ($(BR2_PACKAGE_ALSA_LIB)$(BR2_PACKAGE_ALSA_LIB_SEQ)$(BR2_PACKAGE_ALSA_LIB_RAWMIDI),yyy)
WINE_PROTON_WOW64_32_CONF_OPTS += --with-alsa
WINE_PROTON_WOW64_32_DEPENDENCIES += alsa-lib
else
WINE_PROTON_WOW64_32_CONF_OPTS += --without-alsa
endif

ifeq ($(BR2_PACKAGE_CUPS),y)
WINE_PROTON_WOW64_32_CONF_OPTS += --with-cups
WINE_PROTON_WOW64_32_DEPENDENCIES += cups
WINE_PROTON_WOW64_32_CONF_ENV += CUPS_CONFIG=$(STAGING_DIR)/usr/bin/cups-config
else
WINE_PROTON_WOW64_32_CONF_OPTS += --without-cups
endif

ifeq ($(BR2_PACKAGE_DBUS),y)
WINE_PROTON_WOW64_32_CONF_OPTS += --with-dbus
WINE_PROTON_WOW64_32_DEPENDENCIES += dbus
else
WINE_PROTON_WOW64_32_CONF_OPTS += --without-dbus
endif

ifeq ($(BR2_PACKAGE_FONTCONFIG),y)
WINE_PROTON_WOW64_32_CONF_OPTS += --with-fontconfig
WINE_PROTON_WOW64_32_DEPENDENCIES += fontconfig
else
WINE_PROTON_WOW64_32_CONF_OPTS += --without-fontconfig
endif

# To support freetype in wine we also need freetype in host-wine for the cross compiling tools
ifeq ($(BR2_PACKAGE_FREETYPE),y)
WINE_PROTON_WOW64_32_CONF_OPTS += --with-freetype
HOST_WINE_PROTON_WOW64_32_CONF_OPTS += --with-freetype
WINE_PROTON_WOW64_32_DEPENDENCIES += freetype
HOST_WINE_PROTON_WOW64_32_DEPENDENCIES += host-freetype
WINE_PROTON_WOW64_32_CONF_ENV += FREETYPE_CONFIG=$(STAGING_DIR)/usr/bin/freetype-config
else
WINE_PROTON_WOW64_32_CONF_OPTS += --without-freetype
HOST_WINE_PROTON_WOW64_32_CONF_OPTS += --without-freetype
endif

ifeq ($(BR2_PACKAGE_GNUTLS),y)
WINE_PROTON_WOW64_32_CONF_OPTS += --with-gnutls
WINE_PROTON_WOW64_32_DEPENDENCIES += gnutls
else
WINE_PROTON_WOW64_32_CONF_OPTS += --without-gnutls
endif

ifeq ($(BR2_PACKAGE_GST1_PLUGINS_BASE),y)
WINE_PROTON_WOW64_32_CONF_OPTS += --with-gstreamer
WINE_PROTON_WOW64_32_DEPENDENCIES += gst1-plugins-base
else
WINE_PROTON_WOW64_32_CONF_OPTS += --without-gstreamer
endif

ifeq ($(BR2_PACKAGE_JPEG),y)
WINE_PROTON_WOW64_32_CONF_OPTS += --with-jpeg
WINE_PROTON_WOW64_32_DEPENDENCIES += jpeg
else
WINE_PROTON_WOW64_32_CONF_OPTS += --without-jpeg
endif

ifeq ($(BR2_PACKAGE_LCMS2),y)
WINE_PROTON_WOW64_32_CONF_OPTS += --with-cms
WINE_PROTON_WOW64_32_DEPENDENCIES += lcms2
else
WINE_PROTON_WOW64_32_CONF_OPTS += --without-cms
endif

ifeq ($(BR2_PACKAGE_HAS_LIBGL),y)
WINE_PROTON_WOW64_32_CONF_OPTS += --with-opengl
WINE_PROTON_WOW64_32_DEPENDENCIES += libgl
else
WINE_PROTON_WOW64_32_CONF_OPTS += --without-opengl
endif

ifeq ($(BR2_PACKAGE_LIBGLU),y)
WINE_PROTON_WOW64_32_CONF_OPTS += --with-glu
WINE_PROTON_WOW64_32_DEPENDENCIES += libglu
else
WINE_PROTON_WOW64_32_CONF_OPTS += --without-glu
endif

ifeq ($(BR2_PACKAGE_LIBKRB5),y)
WINE_PROTON_WOW64_32_CONF_OPTS += --with-krb5
WINE_PROTON_WOW64_32_DEPENDENCIES += libkrb5
else
WINE_PROTON_WOW64_32_CONF_OPTS += --without-krb5
endif

ifeq ($(BR2_PACKAGE_LIBPCAP),y)
WINE_PROTON_WOW64_32_CONF_OPTS += --with-pcap
WINE_PROTON_WOW64_32_DEPENDENCIES += libpcap
else
WINE_PROTON_WOW64_32_CONF_OPTS += --without-pcap
endif

ifeq ($(BR2_PACKAGE_LIBPNG),y)
WINE_PROTON_WOW64_32_CONF_OPTS += --with-png
WINE_PROTON_WOW64_32_DEPENDENCIES += libpng
else
WINE_PROTON_WOW64_32_CONF_OPTS += --without-png
endif

ifeq ($(BR2_PACKAGE_LIBV4L),y)
WINE_PROTON_WOW64_32_CONF_OPTS += --with-v4l
WINE_PROTON_WOW64_32_DEPENDENCIES += libv4l
else
WINE_PROTON_WOW64_32_CONF_OPTS += --without-v4l
endif

ifeq ($(BR2_PACKAGE_LIBXML2),y)
WINE_PROTON_WOW64_32_CONF_OPTS += --with-xml
WINE_PROTON_WOW64_32_DEPENDENCIES += libxml2
WINE_PROTON_WOW64_32_CONF_ENV += XML2_CONFIG=$(STAGING_DIR)/usr/bin/xml2-config
else
WINE_PROTON_WOW64_32_CONF_OPTS += --without-xml
endif

ifeq ($(BR2_PACKAGE_LIBXSLT),y)
WINE_PROTON_WOW64_32_CONF_OPTS += --with-xslt
WINE_PROTON_WOW64_32_DEPENDENCIES += libxslt
WINE_PROTON_WOW64_32_CONF_ENV += XSLT_CONFIG=$(STAGING_DIR)/usr/bin/xslt-config
else
WINE_PROTON_WOW64_32_CONF_OPTS += --without-xslt
endif

ifeq ($(BR2_PACKAGE_MPG123),y)
WINE_PROTON_WOW64_32_CONF_OPTS += --with-mpg123
WINE_PROTON_WOW64_32_DEPENDENCIES += mpg123
else
WINE_PROTON_WOW64_32_CONF_OPTS += --without-mpg123
endif

ifeq ($(BR2_PACKAGE_NCURSES),y)
WINE_PROTON_WOW64_32_CONF_OPTS += --with-curses
WINE_PROTON_WOW64_32_DEPENDENCIES += ncurses
else
WINE_PROTON_WOW64_32_CONF_OPTS += --without-curses
endif

ifeq ($(BR2_PACKAGE_OPENAL),y)
WINE_PROTON_WOW64_32_CONF_OPTS += --with-openal
WINE_PROTON_WOW64_32_DEPENDENCIES += openal
else
WINE_PROTON_WOW64_32_CONF_OPTS += --without-openal
endif

ifeq ($(BR2_PACKAGE_OPENLDAP),y)
WINE_PROTON_WOW64_32_CONF_OPTS += --with-ldap
WINE_PROTON_WOW64_32_DEPENDENCIES += openldap
else
WINE_PROTON_WOW64_32_CONF_OPTS += --without-ldap
endif

ifeq ($(BR2_PACKAGE_MESA3D_OSMESA_CLASSIC),y)
WINE_PROTON_WOW64_32_CONF_OPTS += --with-osmesa
WINE_PROTON_WOW64_32_DEPENDENCIES += mesa3d
else
WINE_PROTON_WOW64_32_CONF_OPTS += --without-osmesa
endif

ifeq ($(BR2_PACKAGE_PULSEAUDIO),y)
WINE_PROTON_WOW64_32_CONF_OPTS += --with-pulse
WINE_PROTON_WOW64_32_DEPENDENCIES += pulseaudio
else
WINE_PROTON_WOW64_32_CONF_OPTS += --without-pulse
endif

ifeq ($(BR2_PACKAGE_SAMBA4),y)
WINE_PROTON_WOW64_32_CONF_OPTS += --with-netapi
WINE_PROTON_WOW64_32_DEPENDENCIES += samba4
else
WINE_PROTON_WOW64_32_CONF_OPTS += --without-netapi
endif

ifeq ($(BR2_PACKAGE_SANE_BACKENDS),y)
WINE_PROTON_WOW64_32_CONF_OPTS += --with-sane
WINE_PROTON_WOW64_32_DEPENDENCIES += sane-backends
WINE_PROTON_WOW64_32_CONF_ENV += SANE_CONFIG=$(STAGING_DIR)/usr/bin/sane-config
else
WINE_PROTON_WOW64_32_CONF_OPTS += --without-sane
endif

ifeq ($(BR2_PACKAGE_SDL2),y)
WINE_PROTON_WOW64_32_CONF_OPTS += --with-sdl
WINE_PROTON_WOW64_32_DEPENDENCIES += sdl2
else
WINE_PROTON_WOW64_32_CONF_OPTS += --without-sdl
endif

ifeq ($(BR2_PACKAGE_TIFF),y)
WINE_PROTON_WOW64_32_CONF_OPTS += --with-tiff
WINE_PROTON_WOW64_32_DEPENDENCIES += tiff
else
WINE_PROTON_WOW64_32_CONF_OPTS += --without-tiff
endif

ifeq ($(BR2_PACKAGE_HAS_UDEV),y)
WINE_PROTON_WOW64_32_CONF_OPTS += --with-udev
WINE_PROTON_WOW64_32_DEPENDENCIES += udev
else
WINE_PROTON_WOW64_32_CONF_OPTS += --without-udev
endif

ifeq ($(BR2_PACKAGE_XLIB_LIBX11),y)
WINE_PROTON_WOW64_32_CONF_OPTS += --with-x
WINE_PROTON_WOW64_32_DEPENDENCIES += xlib_libX11
else
WINE_PROTON_WOW64_32_CONF_OPTS += --without-x
endif

ifeq ($(BR2_PACKAGE_XLIB_LIBXCOMPOSITE),y)
WINE_PROTON_WOW64_32_CONF_OPTS += --with-xcomposite
WINE_PROTON_WOW64_32_DEPENDENCIES += xlib_libXcomposite
else
WINE_PROTON_WOW64_32_CONF_OPTS += --without-xcomposite
endif

ifeq ($(BR2_PACKAGE_XLIB_LIBXCURSOR),y)
WINE_PROTON_WOW64_32_CONF_OPTS += --with-xcursor
WINE_PROTON_WOW64_32_DEPENDENCIES += xlib_libXcursor
else
WINE_PROTON_WOW64_32_CONF_OPTS += --without-xcursor
endif

ifeq ($(BR2_PACKAGE_XLIB_LIBXEXT),y)
WINE_PROTON_WOW64_32_CONF_OPTS += --with-xshape --with-xshm
WINE_PROTON_WOW64_32_DEPENDENCIES += xlib_libXext
else
WINE_PROTON_WOW64_32_CONF_OPTS += --without-xshape --without-xshm
endif

ifeq ($(BR2_PACKAGE_XLIB_LIBXI),y)
WINE_PROTON_WOW64_32_CONF_OPTS += --with-xinput --with-xinput2
WINE_PROTON_WOW64_32_DEPENDENCIES += xlib_libXi
else
WINE_PROTON_WOW64_32_CONF_OPTS += --without-xinput --without-xinput2
endif

ifeq ($(BR2_PACKAGE_XLIB_LIBXINERAMA),y)
WINE_PROTON_WOW64_32_CONF_OPTS += --with-xinerama
WINE_PROTON_WOW64_32_DEPENDENCIES += xlib_libXinerama
else
WINE_PROTON_WOW64_32_CONF_OPTS += --without-xinerama
endif

ifeq ($(BR2_PACKAGE_XLIB_LIBXRANDR),y)
WINE_PROTON_WOW64_32_CONF_OPTS += --with-xrandr
WINE_PROTON_WOW64_32_DEPENDENCIES += xlib_libXrandr
else
WINE_PROTON_WOW64_32_CONF_OPTS += --without-xrandr
endif

ifeq ($(BR2_PACKAGE_XLIB_LIBXRENDER),y)
WINE_PROTON_WOW64_32_CONF_OPTS += --with-xrender
WINE_PROTON_WOW64_32_DEPENDENCIES += xlib_libXrender
else
WINE_PROTON_WOW64_32_CONF_OPTS += --without-xrender
endif

ifeq ($(BR2_PACKAGE_XLIB_LIBXXF86VM),y)
WINE_PROTON_WOW64_32_CONF_OPTS += --with-xxf86vm
WINE_PROTON_WOW64_32_DEPENDENCIES += xlib_libXxf86vm
else
WINE_PROTON_WOW64_32_CONF_OPTS += --without-xxf86vm
endif

ifeq ($(BR2_PACKAGE_ZLIB),y)
WINE_PROTON_WOW64_32_CONF_OPTS += --with-zlib
WINE_PROTON_WOW64_32_DEPENDENCIES += zlib
else
WINE_PROTON_WOW64_32_CONF_OPTS += --without-zlib
endif

# host-gettext is essential for .po file support in host-wine wrc
ifeq ($(BR2_SYSTEM_ENABLE_NLS),y)
HOST_WINE_PROTON_WOW64_32_DEPENDENCIES += host-gettext
HOST_WINE_PROTON_WOW64_32_CONF_OPTS += --with-gettext --with-gettextpo
else
HOST_WINE_PROTON_WOW64_32_CONF_OPTS += --without-gettext --without-gettextpo
endif

# Wine needs to enable 64-bit build tools on 64-bit host
ifeq ($(HOSTARCH),x86_64)
HOST_WINE_PROTON_WOW64_32_CONF_OPTS += --enable-win64
endif

# Wine only needs the host tools to be built, so cut-down the
# build time by building just what we need.
define HOST_WINE_PROTON_WOW64_32_BUILD_CMDS
	$(HOST_MAKE_ENV) $(MAKE) -C $(@D) \
	  tools \
	  tools/sfnt2fon \
	  tools/widl \
	  tools/winebuild \
	  tools/winegcc \
	  tools/wmc \
	  tools/wrc
endef

# Wine only needs its host variant to be built, not that it is
# installed, as it uses the tools from the build directory. But
# we have no way in Buildroot to state that a host package should
# not be installed. So, just provide an noop install command.
define HOST_WINE_PROTON_WOW64_32_INSTALL_CMDS
	:
endef

# We are focused on the cross compiling tools, disable everything else
HOST_WINE_PROTON_WOW64_32_CONF_OPTS += \
	--disable-tests \
	--disable-win16 \
	--without-alsa \
	--without-capi \
	--without-cms \
	--without-coreaudio \
	--without-faudio \
	--without-cups \
	--without-curses \
	--without-dbus \
	--without-fontconfig \
	--without-gphoto \
	--without-glu \
	--without-gnutls \
	--without-gsm \
	--without-gssapi \
	--without-gstreamer \
	--without-hal \
	--without-jpeg \
	--without-krb5 \
	--without-ldap \
	--without-mpg123 \
	--without-netapi \
	--without-openal \
	--without-opencl \
	--without-opengl \
	--without-osmesa \
	--without-oss \
	--without-pcap \
	--without-pulse \
	--without-png \
	--without-sane \
	--without-sdl \
	--without-tiff \
	--without-v4l \
	--without-vkd3d \
	--without-vulkan \
	--without-x \
	--without-xcomposite \
	--without-xcursor \
	--without-xinerama \
	--without-xinput \
	--without-xinput2 \
	--without-xml \
	--without-xrandr \
	--without-xrender \
	--without-xshape \
	--without-xshm \
	--without-xslt \
	--without-xxf86vm \
	--without-zlib

define WINE_PROTON_WOW64_32_WOWDIRS_HOOK
	mkdir -p $(BINARIES_DIR)/wow64_32_part64/loader
endef

define WINE_PROTON_WOW64_32_SHAREDIR_HOOK
	mkdir -p $(TARGET_DIR)/share/wine/
	cp -pr $(@D)/nls $(TARGET_DIR)/share/wine/
	rm -Rf $(TARGET_DIR)/usr/wine/proton/include
endef

WINE_PROTON_WOW64_32_PRE_BUILD_HOOKS += WINE_PROTON_WOW64_32_WOWDIRS_HOOK
WINE_PROTON_WOW64_32_POST_INSTALL_TARGET_HOOKS += WINE_PROTON_WOW64_32_SHAREDIR_HOOK

$(eval $(autotools-package))
$(eval $(host-autotools-package))
