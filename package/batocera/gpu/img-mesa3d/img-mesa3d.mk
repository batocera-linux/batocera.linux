################################################################################
#
# mesa3d
#
################################################################################

# When updating the version, please also update mesa3d-headers
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

# the src/mesa/main/formats.csv in mesa-22.1.3 offical tarball is msdos file format
# patch the 0023-dri-add-support-for-YUV-DRI-config.patch will failed:
#      Hunk #1 FAILED at 92 (different line endings).
# so first change to the unix file format before patch
define IMG_MESA3D_CHANEG_FILE_TO_UNIX_FORMAT
	if [ -f $(@D)/src/mesa/main/formats.csv ]; then \
		sed -i 's/\r$$//' $(@D)/src/mesa/main/formats.csv; \
	fi
endef

IMG_MESA3D_POST_EXTRACT_HOOKS += IMG_MESA3D_CHANEG_FILE_TO_UNIX_FORMAT

IMG_MESA3D_CONF_OPTS = \
	-Dgallium-omx=disabled \
	-Dpower8=disabled

# Codesourcery ARM 2014.05 fail to link libmesa_dri_drivers.so with --as-needed linker
# flag due to a linker bug between binutils 2.24 and 2.25 (2.24.51.20140217).
ifeq ($(BR2_TOOLCHAIN_EXTERNAL_CODESOURCERY_ARM),y)
IMG_MESA3D_CONF_OPTS += -Db_asneeded=false
endif

ifeq ($(BR2_PACKAGE_IMG_MESA3D_DRI3),y)
IMG_MESA3D_CONF_OPTS += -Ddri3=enabled
ifeq ($(BR2_PACKAGE_XLIB_LIBXSHMFENCE),y)
IMG_MESA3D_DEPENDENCIES += xlib_libxshmfence
endif
else
IMG_MESA3D_CONF_OPTS += -Ddri3=disabled
endif

ifeq ($(BR2_PACKAGE_IMG_MESA3D_LLVM),y)
IMG_MESA3D_DEPENDENCIES += host-llvm llvm
IMG_MESA3D_MESON_EXTRA_BINARIES += llvm-config='$(STAGING_DIR)/usr/bin/llvm-config'
IMG_MESA3D_CONF_OPTS += -Dllvm=enabled
else
# Avoid automatic search of llvm-config
IMG_MESA3D_CONF_OPTS += -Dllvm=disabled
endif

# Disable opencl-icd: OpenCL lib will be named libOpenCL instead of
# libMesaOpenCL and CL headers are installed
ifeq ($(BR2_PACKAGE_IMG_MESA3D_OPENCL),y)
IMG_MESA3D_PROVIDES += libopencl
IMG_MESA3D_DEPENDENCIES += clang libclc
IMG_MESA3D_CONF_OPTS += -Dgallium-opencl=standalone
else
IMG_MESA3D_CONF_OPTS += -Dgallium-opencl=disabled
endif

ifeq ($(BR2_PACKAGE_IMG_MESA3D_NEEDS_ELFUTILS),y)
IMG_MESA3D_DEPENDENCIES += elfutils
endif

ifeq ($(BR2_PACKAGE_IMG_MESA3D_OPENGL_GLX),y)
# Disable-mangling not yet supported by meson build system.
# glx:
#  dri          : dri based GLX requires at least one DRI driver || dri based GLX requires shared-glapi
#  xlib         : xlib conflicts with any dri driver
#  gallium-xlib : Gallium-xlib based GLX requires at least one gallium driver || Gallium-xlib based GLX requires softpipe or llvmpipe || gallium-xlib conflicts with any dri driver.
# Always enable glx-direct; without it, many GLX applications don't work.
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

# ifeq ($(BR2_ARM_CPU_HAS_NEON),y)
# IMG_MESA3D_CONF_OPTS += -Dgallium-vc4-neon=auto
# else
# IMG_MESA3D_CONF_OPTS += -Dgallium-vc4-neon=disabled
# endif

# Drivers

#Gallium Drivers
IMG_MESA3D_GALLIUM_DRIVERS-$(BR2_PACKAGE_IMG_MESA3D_GALLIUM_DRIVER_CROCUS)   += crocus
IMG_MESA3D_GALLIUM_DRIVERS-$(BR2_PACKAGE_IMG_MESA3D_GALLIUM_DRIVER_ETNAVIV)  += etnaviv
IMG_MESA3D_GALLIUM_DRIVERS-$(BR2_PACKAGE_IMG_MESA3D_GALLIUM_DRIVER_FREEDRENO) += freedreno
IMG_MESA3D_GALLIUM_DRIVERS-$(BR2_PACKAGE_IMG_MESA3D_GALLIUM_DRIVER_I915)     += i915
IMG_MESA3D_GALLIUM_DRIVERS-$(BR2_PACKAGE_IMG_MESA3D_GALLIUM_DRIVER_IRIS)     += iris
IMG_MESA3D_GALLIUM_DRIVERS-$(BR2_PACKAGE_IMG_MESA3D_GALLIUM_DRIVER_LIMA)     += lima
IMG_MESA3D_GALLIUM_DRIVERS-$(BR2_PACKAGE_IMG_MESA3D_GALLIUM_DRIVER_NOUVEAU)  += nouveau
IMG_MESA3D_GALLIUM_DRIVERS-$(BR2_PACKAGE_IMG_MESA3D_GALLIUM_DRIVER_PANFROST) += panfrost
IMG_MESA3D_GALLIUM_DRIVERS-$(BR2_PACKAGE_IMG_MESA3D_GALLIUM_DRIVER_R300)     += r300
IMG_MESA3D_GALLIUM_DRIVERS-$(BR2_PACKAGE_IMG_MESA3D_GALLIUM_DRIVER_R600)     += r600
IMG_MESA3D_GALLIUM_DRIVERS-$(BR2_PACKAGE_IMG_MESA3D_GALLIUM_DRIVER_RADEONSI) += radeonsi
IMG_MESA3D_GALLIUM_DRIVERS-$(BR2_PACKAGE_IMG_MESA3D_GALLIUM_DRIVER_SVGA)     += svga
IMG_MESA3D_GALLIUM_DRIVERS-$(BR2_PACKAGE_IMG_MESA3D_GALLIUM_DRIVER_SWRAST)   += swrast
IMG_MESA3D_GALLIUM_DRIVERS-$(BR2_PACKAGE_IMG_MESA3D_GALLIUM_DRIVER_TEGRA)    += tegra
IMG_MESA3D_GALLIUM_DRIVERS-$(BR2_PACKAGE_IMG_MESA3D_GALLIUM_DRIVER_V3D)      += v3d
IMG_MESA3D_GALLIUM_DRIVERS-$(BR2_PACKAGE_IMG_MESA3D_GALLIUM_DRIVER_VC4)      += vc4
IMG_MESA3D_GALLIUM_DRIVERS-$(BR2_PACKAGE_IMG_MESA3D_GALLIUM_DRIVER_VIRGL)    += virgl
IMG_MESA3D_GALLIUM_DRIVERS-$(BR2_PACKAGE_IMG_MESA3D_GALLIUM_DRIVER_PVR)      += pvr
# Vulkan Drivers
IMG_MESA3D_VULKAN_DRIVERS-$(BR2_PACKAGE_IMG_MESA3D_VULKAN_DRIVER_INTEL)   += intel

ifeq ($(BR2_PACKAGE_IMG_MESA3D_GALLIUM_DRIVER),)
IMG_MESA3D_CONF_OPTS += \
	-Dgallium-drivers= \
	-Dgallium-extra-hud=false
else
IMG_MESA3D_CONF_OPTS += \
	-Dshared-glapi=enabled \
	-Dgallium-drivers=$(subst $(space),$(comma),$(IMG_MESA3D_GALLIUM_DRIVERS-y)) \
	-Dgallium-extra-hud=true
ifeq ($(BR2_PACKAGE_IMG_MESA3D_GALLIUM_DRIVER_PVR),y)
IMG_MESA3D_DEPENDENCIES += img-gpu-powervr
endif
endif

ifeq ($(BR2_PACKAGE_IMG_MESA3D_VULKAN_DRIVER),)
IMG_MESA3D_CONF_OPTS += \
	-Dvulkan-drivers=
else
IMG_MESA3D_CONF_OPTS += \
	-Dvulkan-drivers=$(subst $(space),$(comma),$(IMG_MESA3D_VULKAN_DRIVERS-y))
endif

# APIs

ifeq ($(BR2_PACKAGE_IMG_MESA3D_OSMESA_GALLIUM),y)
IMG_MESA3D_CONF_OPTS += -Dosmesa=true
else
IMG_MESA3D_CONF_OPTS += -Dosmesa=false
endif

# Always enable OpenGL:
#   - Building OpenGL ES without OpenGL is not supported, so always keep opengl enabled.
IMG_MESA3D_CONF_OPTS += -Dopengl=true

# libva and mesa3d have a circular dependency
# we do not need libva support in mesa3d, therefore disable this option
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

ifeq ($(BR2_PACKAGE_IMG_MESA3D_VDPAU),y)
IMG_MESA3D_DEPENDENCIES += libvdpau
IMG_MESA3D_CONF_OPTS += -Dgallium-vdpau=enabled
else
IMG_MESA3D_CONF_OPTS += -Dgallium-vdpau=disabled
endif

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

# m68k needs 32-bit offsets in switch tables to build
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
