################################################################################
#
# mesa3d
#
################################################################################

MESA_PANFORK_VERSION = 120202c675749c5ef81ae4c8cdc30019b4de08f4
#MESA_PANFORK_SOURCE = mesa-$(MESA_PANFORK_VERSION).tar.xz
MESA_PANFORK_SITE = https://gitlab.com/panfork/mesa.git
MESA_PANFORK_SITE_METHOD = git
MESA_PANFORK_LICENSE = MIT, SGI, Khronos
MESA_PANFORK_LICENSE_FILES = docs/license.rst
MESA_PANFORK_CPE_ID_VENDOR = mesa3d
MESA_PANFORK_CPE_ID_PRODUCT = mesa

MESA_PANFORK_INSTALL_STAGING = YES

MESA_PANFORK_PROVIDES =

MESA_PANFORK_DEPENDENCIES = \
	host-bison \
	host-flex \
	host-python-mako \
	expat \
	libdrm \
	zlib

# the src/mesa/main/formats.csv in mesa-22.1.3 offical tarball is msdos file format
# patch the 0023-dri-add-support-for-YUV-DRI-config.patch will failed:
#      Hunk #1 FAILED at 92 (different line endings).
# so first change to the unix file format before patch
define MESA_PANFORK_CHANEG_FILE_TO_UNIX_FORMAT
	if [ -f $(@D)/src/mesa/main/formats.csv ]; then \
		sed -i 's/\r$$//' $(@D)/src/mesa/main/formats.csv; \
	fi
endef

MESA_PANFORK_POST_EXTRACT_HOOKS += MESA_PANFORK_CHANEG_FILE_TO_UNIX_FORMAT

MESA_PANFORK_CONF_OPTS = \
	-Dgallium-omx=disabled \
	-Dpower8=disabled

# Codesourcery ARM 2014.05 fail to link libmesa_dri_drivers.so with --as-needed linker
# flag due to a linker bug between binutils 2.24 and 2.25 (2.24.51.20140217).
ifeq ($(BR2_TOOLCHAIN_EXTERNAL_CODESOURCERY_ARM),y)
MESA_PANFORK_CONF_OPTS += -Db_asneeded=false
endif

ifeq ($(BR2_PACKAGE_MESA_PANFORK_DRI3),y)
MESA_PANFORK_CONF_OPTS += -Ddri3=enabled
ifeq ($(BR2_PACKAGE_XLIB_LIBXSHMFENCE),y)
MESA_PANFORK_DEPENDENCIES += xlib_libxshmfence
endif
else
MESA_PANFORK_CONF_OPTS += -Ddri3=disabled
endif

ifeq ($(BR2_PACKAGE_MESA_PANFORK_LLVM),y)
MESA_PANFORK_DEPENDENCIES += host-llvm llvm
MESA_PANFORK_MESON_EXTRA_BINARIES += llvm-config='$(STAGING_DIR)/usr/bin/llvm-config'
MESA_PANFORK_CONF_OPTS += -Dllvm=enabled
else
# Avoid automatic search of llvm-config
MESA_PANFORK_CONF_OPTS += -Dllvm=disabled
endif

# Disable opencl-icd: OpenCL lib will be named libOpenCL instead of
# libMesaOpenCL and CL headers are installed
ifeq ($(BR2_PACKAGE_MESA_PANFORK_OPENCL),y)
MESA_PANFORK_PROVIDES += libopencl
MESA_PANFORK_DEPENDENCIES += clang libclc
MESA_PANFORK_CONF_OPTS += -Dgallium-opencl=standalone
else
MESA_PANFORK_CONF_OPTS += -Dgallium-opencl=disabled
endif

ifeq ($(BR2_PACKAGE_MESA_PANFORK_NEEDS_ELFUTILS),y)
MESA_PANFORK_DEPENDENCIES += elfutils
endif

ifeq ($(BR2_PACKAGE_MESA_PANFORK_OPENGL_GLX),y)
# Disable-mangling not yet supported by meson build system.
# glx:
#  dri          : dri based GLX requires at least one DRI driver || dri based GLX requires shared-glapi
#  xlib         : xlib conflicts with any dri driver
#  gallium-xlib : Gallium-xlib based GLX requires at least one gallium driver || Gallium-xlib based GLX requires softpipe or llvmpipe || gallium-xlib conflicts with any dri driver.
# Always enable glx-direct; without it, many GLX applications don't work.
MESA_PANFORK_CONF_OPTS += \
	-Dglx=dri \
	-Dglx-direct=true
ifeq ($(BR2_PACKAGE_MESA_PANFORK_NEEDS_XA),y)
MESA_PANFORK_CONF_OPTS += -Dgallium-xa=enabled
else
MESA_PANFORK_CONF_OPTS += -Dgallium-xa=disabled
endif
else
MESA_PANFORK_CONF_OPTS += \
	-Dglx=disabled \
	-Dgallium-xa=disabled
endif

# Drivers

#Gallium Drivers
MESA_PANFORK_GALLIUM_DRIVERS-$(BR2_PACKAGE_MESA_PANFORK_GALLIUM_DRIVER_PANFROST) += panfrost

ifeq ($(BR2_PACKAGE_MESA_PANFORK_GALLIUM_DRIVER),)
MESA_PANFORK_CONF_OPTS += \
	-Dgallium-drivers= \
	-Dgallium-extra-hud=false
else
MESA_PANFORK_CONF_OPTS += \
	-Dshared-glapi=enabled \
	-Dgallium-drivers=$(subst $(space),$(comma),$(MESA_PANFORK_GALLIUM_DRIVERS-y)) \
	-Dgallium-extra-hud=true
endif

ifeq ($(BR2_PACKAGE_MESA_PANFORK_VULKAN_DRIVER),)
MESA_PANFORK_CONF_OPTS += \
	-Dvulkan-drivers=
else
MESA_PANFORK_CONF_OPTS += \
	-Dvulkan-drivers=$(subst $(space),$(comma),$(MESA_PANFORK_VULKAN_DRIVERS-y))
endif

# APIs

ifeq ($(BR2_PACKAGE_MESA_PANFORK_OSMESA_GALLIUM),y)
MESA_PANFORK_CONF_OPTS += -Dosmesa=true
else
MESA_PANFORK_CONF_OPTS += -Dosmesa=false
endif

# Always enable OpenGL:
#   - Building OpenGL ES without OpenGL is not supported, so always keep opengl enabled.
MESA_PANFORK_CONF_OPTS += -Dopengl=true

# libva and mesa3d have a circular dependency
# we do not need libva support in mesa3d, therefore disable this option
MESA_PANFORK_CONF_OPTS += -Dgallium-va=disabled

# libGL is only provided for a full xorg stack, without libglvnd
ifeq ($(BR2_PACKAGE_MESA_PANFORK_OPENGL_GLX),y)
MESA_PANFORK_PROVIDES += $(if $(BR2_PACKAGE_LIBGLVND),,libgl)
else
define MESA_PANFORK_REMOVE_OPENGL_HEADERS
	rm -rf $(STAGING_DIR)/usr/include/GL/
endef

MESA_PANFORK_POST_INSTALL_STAGING_HOOKS += MESA_PANFORK_REMOVE_OPENGL_HEADERS
endif

ifeq ($(BR2_PACKAGE_WAYLAND),y)
MESA_PANFORK_DEPENDENCIES += wayland wayland-protocols
MESA_PANFORK_PLATFORMS += wayland
endif

MESA_PANFORK_CONF_OPTS += \
	-Dplatforms=$(subst $(space),$(comma),$(MESA_PANFORK_PLATFORMS))

ifeq ($(BR2_PACKAGE_MESA_PANFORK_GBM),y)
MESA_PANFORK_CONF_OPTS += \
	-Dgbm=enabled
else
MESA_PANFORK_CONF_OPTS += \
	-Dgbm=disabled
endif

ifeq ($(BR2_PACKAGE_MESA_PANFORK_OPENGL_EGL),y)
MESA_PANFORK_PROVIDES += $(if $(BR2_PACKAGE_LIBGLVND),,libegl)
MESA_PANFORK_CONF_OPTS += \
	-Degl=enabled
else
MESA_PANFORK_CONF_OPTS += \
	-Degl=disabled
endif

ifeq ($(BR2_PACKAGE_MESA_PANFORK_OPENGL_ES),y)
MESA_PANFORK_PROVIDES += $(if $(BR2_PACKAGE_LIBGLVND),,libgles)
MESA_PANFORK_CONF_OPTS += -Dgles1=enabled -Dgles2=enabled
else
MESA_PANFORK_CONF_OPTS += -Dgles1=disabled -Dgles2=disabled
endif

ifeq ($(BR2_PACKAGE_VALGRIND),y)
MESA_PANFORK_CONF_OPTS += -Dvalgrind=enabled
MESA_PANFORK_DEPENDENCIES += valgrind
else
MESA_PANFORK_CONF_OPTS += -Dvalgrind=disabled
endif

ifeq ($(BR2_PACKAGE_LIBUNWIND),y)
MESA_PANFORK_CONF_OPTS += -Dlibunwind=enabled
MESA_PANFORK_DEPENDENCIES += libunwind
else
MESA_PANFORK_CONF_OPTS += -Dlibunwind=disabled
endif

ifeq ($(BR2_PACKAGE_MESA_PANFORK_VDPAU),y)
MESA_PANFORK_DEPENDENCIES += libvdpau
MESA_PANFORK_CONF_OPTS += -Dgallium-vdpau=enabled
else
MESA_PANFORK_CONF_OPTS += -Dgallium-vdpau=disabled
endif

ifeq ($(BR2_PACKAGE_LM_SENSORS),y)
MESA_PANFORK_CONF_OPTS += -Dlmsensors=enabled
MESA_PANFORK_DEPENDENCIES += lm-sensors
else
MESA_PANFORK_CONF_OPTS += -Dlmsensors=disabled
endif

ifeq ($(BR2_PACKAGE_ZSTD),y)
MESA_PANFORK_CONF_OPTS += -Dzstd=enabled
MESA_PANFORK_DEPENDENCIES += zstd
else
MESA_PANFORK_CONF_OPTS += -Dzstd=disabled
endif

MESA_PANFORK_CFLAGS = $(TARGET_CFLAGS)

# m68k needs 32-bit offsets in switch tables to build
ifeq ($(BR2_m68k),y)
MESA_PANFORK_CFLAGS += -mlong-jump-table-offsets
endif

ifeq ($(BR2_PACKAGE_LIBGLVND),y)
ifneq ($(BR2_PACKAGE_MESA_PANFORK_OPENGL_GLX)$(BR2_PACKAGE_MESA_PANFORK_OPENGL_EGL),)
MESA_PANFORK_DEPENDENCIES += libglvnd
MESA_PANFORK_CONF_OPTS += -Dglvnd=true
else
MESA_PANFORK_CONF_OPTS += -Dglvnd=false
endif
else
MESA_PANFORK_CONF_OPTS += -Dglvnd=false
endif

$(eval $(meson-package))
