################################################################################
#
# img-mesa3d
#
################################################################################

IMG_MESA3D_VERSION = 22.1.3
IMG_MESA3D_SOURCE = mesa-$(IMG_MESA3D_VERSION).tar.xz
IMG_MESA3D_SITE = https://archive.mesa3d.org
IMG_MESA3D_LICENSE = MIT, SGI, Khronos
IMG_MESA3D_LICENSE_FILES = docs/license.rst
IMG_MESA3D_CPE_ID_VENDOR = mesa3d
IMG_MESA3D_CPE_ID_PRODUCT = mesa

IMG_MESA3D_INSTALL_STAGING = YES

IMG_MESA3D_PROVIDES =

IMG_MESA3D_DEPENDENCIES = \
	host-bison \
	host-flex \
	host-python-mako \
	expat \
	libdrm \
	zlib

define IMG_MESA3D_CHANEG_FILE_TO_UNIX_FORMAT
	if [ -f $(@D)/src/mesa/main/formats.csv ]; then \
		sed -i 's/\r$$//' $(@D)/src/mesa/main/formats.csv; \
	fi
endef

IMG_MESA3D_POST_EXTRACT_HOOKS += IMG_MESA3D_CHANEG_FILE_TO_UNIX_FORMAT

IMG_MESA3D_CONF_OPTS = \
	-Dgallium-omx=disabled \
	-Dpower8=disabled

ifeq ($(BR2_TOOLCHAIN_EXTERNAL_CODESOURCERY_ARM),y)
    IMG_MESA3D_CONF_OPTS += -Db_asneeded=false
endif

IMG_MESA3D_CONF_OPTS += -Ddri3=disabled
IMG_MESA3D_CONF_OPTS += -Dllvm=disabled
IMG_MESA3D_CONF_OPTS += -Dgallium-opencl=disabled

ifeq ($(BR2_PACKAGE_IMG_MESA3D_NEEDS_ELFUTILS),y)
IMG_MESA3D_DEPENDENCIES += elfutils
endif

ifeq ($(BR2_PACKAGE_IMG_MESA3D_OPENGL_GLX),y)
    IMG_MESA3D_CONF_OPTS += \
	    -Dglx=dri \
		-Dglx-direct=true
	ifeq ($(BR2_PACKAGE_IMG_MESA3D_NEEDS_XA),y)
        IMG_MESA3D_CONF_OPTS += -Dgallium-xa=enabled
	else
        IMG_MESA3D_CONF_OPTS += -Dgallium-xa=disabled
	endif
else
    IMG_MESA3D_CONF_OPTS += \
	    -Dglx=disabled \
		-Dgallium-xa=disabled
endif

# Imagination Gallium Driver
IMG_MESA3D_GALLIUM_DRIVERS-$(BR2_PACKAGE_IMG_MESA3D_GALLIUM_DRIVER_PVR) += pvr

ifeq ($(BR2_PACKAGE_IMG_MESA3D_GALLIUM_DRIVER),)
    IMG_MESA3D_CONF_OPTS += \
	    -Dgallium-drivers= \
		-Dgallium-extra-hud=false
else
    IMG_MESA3D_CONF_OPTS += \
	    -Dshared-glapi=enabled \
		-Dgallium-drivers=$(subst $(space),$(comma),$(IMG_MESA3D_GALLIUM_DRIVERS-y)) \
		-Dgallium-extra-hud=true
endif

IMG_MESA3D_CONF_OPTS += -Dvulkan-drivers=

# APIs

ifeq ($(BR2_PACKAGE_IMG_MESA3D_OSMESA_GALLIUM),y)
IMG_MESA3D_CONF_OPTS += -Dosmesa=true
else
IMG_MESA3D_CONF_OPTS += -Dosmesa=false
endif

IMG_MESA3D_CONF_OPTS += -Dopengl=true
IMG_MESA3D_CONF_OPTS += -Dgallium-va=disabled

# libGL is only provided for a full xorg stack, without libglvnd
ifeq ($(BR2_PACKAGE_IMG_MESA3D_OPENGL_GLX),y)
IMG_MESA3D_PROVIDES += $(if $(BR2_PACKAGE_LIBGLVND),,libgl)
else
define IMG_MESA3D_REMOVE_OPENGL_HEADERS
	rm -rf $(STAGING_DIR)/usr/include/GL/
endef

IMG_MESA3D_POST_INSTALL_STAGING_HOOKS += IMG_MESA3D_REMOVE_OPENGL_HEADERS
endif

ifeq ($(BR2_PACKAGE_IMG_MESA3D_NEEDS_X11),y)
IMG_MESA3D_DEPENDENCIES += \
	xlib_libX11 \
	xlib_libXext \
	xlib_libXdamage \
	xlib_libXfixes \
	xlib_libXrandr \
	xlib_libXxf86vm \
	xorgproto \
	libxcb
IMG_MESA3D_PLATFORMS += x11
endif

ifeq ($(BR2_PACKAGE_WAYLAND),y)
IMG_MESA3D_DEPENDENCIES += wayland wayland-protocols
IMG_MESA3D_PLATFORMS += wayland
endif

IMG_MESA3D_CONF_OPTS += \
	-Dplatforms=$(subst $(space),$(comma),$(IMG_MESA3D_PLATFORMS))

ifeq ($(BR2_PACKAGE_IMG_MESA3D_GBM),y)
IMG_MESA3D_CONF_OPTS += \
	-Dgbm=enabled
else
IMG_MESA3D_CONF_OPTS += \
	-Dgbm=disabled
endif

ifeq ($(BR2_PACKAGE_IMG_MESA3D_OPENGL_EGL),y)
IMG_MESA3D_PROVIDES += $(if $(BR2_PACKAGE_LIBGLVND),,libegl)
IMG_MESA3D_CONF_OPTS += \
	-Degl=enabled
else
IMG_MESA3D_CONF_OPTS += \
	-Degl=disabled
endif

ifeq ($(BR2_PACKAGE_IMG_MESA3D_OPENGL_ES),y)
IMG_MESA3D_PROVIDES += $(if $(BR2_PACKAGE_LIBGLVND),,libgles)
IMG_MESA3D_CONF_OPTS += -Dgles1=enabled -Dgles2=enabled
else
IMG_MESA3D_CONF_OPTS += -Dgles1=disabled -Dgles2=disabled
endif

ifeq ($(BR2_PACKAGE_IMG_MESA3D_XVMC),y)
IMG_MESA3D_DEPENDENCIES += xlib_libXv xlib_libXvMC
IMG_MESA3D_CONF_OPTS += -Dgallium-xvmc=enabled
else
IMG_MESA3D_CONF_OPTS += -Dgallium-xvmc=disabled
endif

ifeq ($(BR2_PACKAGE_VALGRIND),y)
IMG_MESA3D_CONF_OPTS += -Dvalgrind=enabled
IMG_MESA3D_DEPENDENCIES += valgrind
else
IMG_MESA3D_CONF_OPTS += -Dvalgrind=disabled
endif

ifeq ($(BR2_PACKAGE_LIBUNWIND),y)
IMG_MESA3D_CONF_OPTS += -Dlibunwind=enabled
IMG_MESA3D_DEPENDENCIES += libunwind
else
IMG_MESA3D_CONF_OPTS += -Dlibunwind=disabled
endif

IMG_MESA3D_CONF_OPTS += -Dgallium-vdpau=disabled

ifeq ($(BR2_PACKAGE_LM_SENSORS),y)
IMG_MESA3D_CONF_OPTS += -Dlmsensors=enabled
IMG_MESA3D_DEPENDENCIES += lm-sensors
else
IMG_MESA3D_CONF_OPTS += -Dlmsensors=disabled
endif

ifeq ($(BR2_PACKAGE_ZSTD),y)
IMG_MESA3D_CONF_OPTS += -Dzstd=enabled
IMG_MESA3D_DEPENDENCIES += zstd
else
IMG_MESA3D_CONF_OPTS += -Dzstd=disabled
endif

IMG_MESA3D_CFLAGS = $(TARGET_CFLAGS)

ifeq ($(BR2_m68k),y)
IMG_MESA3D_CFLAGS += -mlong-jump-table-offsets
endif

ifeq ($(BR2_PACKAGE_LIBGLVND),y)
ifneq ($(BR2_PACKAGE_IMG_MESA3D_OPENGL_GLX)$(BR2_PACKAGE_IMG_MESA3D_OPENGL_EGL),)
IMG_MESA3D_DEPENDENCIES += libglvnd
IMG_MESA3D_CONF_OPTS += -Dglvnd=true
else
IMG_MESA3D_CONF_OPTS += -Dglvnd=false
endif
else
IMG_MESA3D_CONF_OPTS += -Dglvnd=false
endif

$(eval $(meson-package))
