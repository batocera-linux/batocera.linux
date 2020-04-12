################################################################################
#
# nvidia-driver
#
################################################################################

BATOCERA_NVIDIA_DRIVER_VERSION = 440.82
BATOCERA_NVIDIA_DRIVER_SUFFIX = $(if $(BR2_x86_64),_64)
BATOCERA_NVIDIA_DRIVER_SITE = http://download.nvidia.com/XFree86/Linux-x86$(BATOCERA_NVIDIA_DRIVER_SUFFIX)/$(BATOCERA_NVIDIA_DRIVER_VERSION)
BATOCERA_NVIDIA_DRIVER_SOURCE = NVIDIA-Linux-x86$(BATOCERA_NVIDIA_DRIVER_SUFFIX)-$(BATOCERA_NVIDIA_DRIVER_VERSION).run
BATOCERA_NVIDIA_DRIVER_LICENSE = NVIDIA Software License
BATOCERA_NVIDIA_DRIVER_LICENSE_FILES = LICENSE
BATOCERA_NVIDIA_DRIVER_REDISTRIBUTE = NO
BATOCERA_NVIDIA_DRIVER_INSTALL_STAGING = YES

ifeq ($(BR2_PACKAGE_BATOCERA_NVIDIA_DRIVER_XORG),y)

# Since nvidia-driver are binary blobs, the below dependencies are not
# strictly speaking build dependencies of nvidia-driver. However, they
# are build dependencies of packages that depend on nvidia-driver, so
# they should be built prior to those packages, and the only simple
# way to do so is to make nvidia-driver depend on them.
#batocera enable nvidia-driver and mesa3d to coexist in the same fs
BATOCERA_NVIDIA_DRIVER_DEPENDENCIES = mesa3d xlib_libX11 xlib_libXext libglvnd
# BATOCERA_NVIDIA_DRIVER_PROVIDES = libgl libegl libgles

# batocera modified to suport the vendor-neutral "dispatching" API/ABI
#   https://github.com/aritger/linux-opengl-abi-proposal/blob/master/linux-opengl-abi-proposal.txt
#batocera generic GL libraries are provided by libglvnd
#batocera only vendor version are installed
BATOCERA_NVIDIA_DRIVER_LIBS_GL = \
	libGLX_nvidia.so.$(BATOCERA_NVIDIA_DRIVER_VERSION)

BATOCERA_NVIDIA_DRIVER_LIBS_EGL = \
	libEGL_nvidia.so.$(BATOCERA_NVIDIA_DRIVER_VERSION)

BATOCERA_NVIDIA_DRIVER_LIBS_GLES = \
	libGLESv1_CM_nvidia.so.$(BATOCERA_NVIDIA_DRIVER_VERSION) \
	libGLESv2_nvidia.so.$(BATOCERA_NVIDIA_DRIVER_VERSION)

#batocera libnvidia-egl-wayland soname bump
BATOCERA_NVIDIA_DRIVER_LIBS_MISC = \
	libnvidia-eglcore.so.$(BATOCERA_NVIDIA_DRIVER_VERSION) \
	libnvidia-egl-wayland.so.1.1.4 \
	libnvidia-glcore.so.$(BATOCERA_NVIDIA_DRIVER_VERSION) \
	libnvidia-glsi.so.$(BATOCERA_NVIDIA_DRIVER_VERSION) \
	libnvidia-tls.so.$(BATOCERA_NVIDIA_DRIVER_VERSION) \
	libvdpau_nvidia.so.$(BATOCERA_NVIDIA_DRIVER_VERSION) \
	libnvidia-ml.so.$(BATOCERA_NVIDIA_DRIVER_VERSION)

BATOCERA_NVIDIA_DRIVER_LIBS += \
	$(BATOCERA_NVIDIA_DRIVER_LIBS_GL) \
	$(BATOCERA_NVIDIA_DRIVER_LIBS_EGL) \
	$(BATOCERA_NVIDIA_DRIVER_LIBS_GLES) \
	$(BATOCERA_NVIDIA_DRIVER_LIBS_MISC)

# batocera 32bit libraries
BATOCERA_NVIDIA_DRIVER_32 = \
	$(BATOCERA_NVIDIA_DRIVER_LIBS_GL) \
	$(BATOCERA_NVIDIA_DRIVER_LIBS_EGL) \
	$(BATOCERA_NVIDIA_DRIVER_LIBS_GLES) \
	libnvidia-eglcore.so.$(BATOCERA_NVIDIA_DRIVER_VERSION) \
	libnvidia-glcore.so.$(BATOCERA_NVIDIA_DRIVER_VERSION) \
	libnvidia-glsi.so.$(BATOCERA_NVIDIA_DRIVER_VERSION) \
	libnvidia-tls.so.$(BATOCERA_NVIDIA_DRIVER_VERSION) \
	libvdpau_nvidia.so.$(BATOCERA_NVIDIA_DRIVER_VERSION) \
	libnvidia-ml.so.$(BATOCERA_NVIDIA_DRIVER_VERSION)

# Install the gl.pc file
define BATOCERA_NVIDIA_DRIVER_INSTALL_GL_DEV
	$(INSTALL) -D -m 0644 $(@D)/libGL.la $(STAGING_DIR)/usr/lib/libGL.la
	$(SED) 's:__GENERATED_BY__:Buildroot:' $(STAGING_DIR)/usr/lib/libGL.la
	$(SED) 's:__LIBGL_PATH__:/usr/lib:' $(STAGING_DIR)/usr/lib/libGL.la
	$(SED) 's:-L[^[:space:]]\+::' $(STAGING_DIR)/usr/lib/libGL.la
	$(INSTALL) -D -m 0644 $(BR2_EXTERNAL_BATOCERA_PATH)/package/nvidia-driver/gl.pc $(STAGING_DIR)/usr/lib/pkgconfig/gl.pc
	$(INSTALL) -D -m 0644 $(BR2_EXTERNAL_BATOCERA_PATH)/package/nvidia-driver/egl.pc $(STAGING_DIR)/usr/lib/pkgconfig/egl.pc
endef

# Those libraries are 'private' libraries requiring an agreement with
# NVidia to develop code for those libs. There seems to be no restriction
# on using those libraries (e.g. if the user has such an agreement, or
# wants to run a third-party program developped under such an agreement).
ifeq ($(BR2_PACKAGE_BATOCERA_NVIDIA_DRIVER_PRIVATE_LIBS),y)
BATOCERA_NVIDIA_DRIVER_LIBS += \
	libnvidia-ifr.so.$(BATOCERA_NVIDIA_DRIVER_VERSION) \
	libnvidia-fbc.so.$(BATOCERA_NVIDIA_DRIVER_VERSION)
endif

# We refer to the destination path; the origin file has no directory component
# batocera libnvidia-wfb removed in 418.43
BATOCERA_NVIDIA_DRIVER_X_MODS = \
	drivers/nvidia_drv.so
#	libnvidia-wfb.so.$(BATOCERA_NVIDIA_DRIVER_VERSION)
endif # X drivers

ifeq ($(BR2_PACKAGE_BATOCERA_NVIDIA_DRIVER_CUDA),y)
BATOCERA_NVIDIA_DRIVER_LIBS += \
	libcuda.so.$(BATOCERA_NVIDIA_DRIVER_VERSION) \
	libnvidia-compiler.so.$(BATOCERA_NVIDIA_DRIVER_VERSION) \
	libnvcuvid.so.$(BATOCERA_NVIDIA_DRIVER_VERSION) \
	libnvidia-fatbinaryloader.so.$(BATOCERA_NVIDIA_DRIVER_VERSION) \
	libnvidia-ptxjitcompiler.so.$(BATOCERA_NVIDIA_DRIVER_VERSION) \
	libnvidia-encode.so.$(BATOCERA_NVIDIA_DRIVER_VERSION)
ifeq ($(BR2_PACKAGE_BATOCERA_NVIDIA_DRIVER_CUDA_PROGS),y)
BATOCERA_NVIDIA_DRIVER_PROGS = nvidia-cuda-mps-control nvidia-cuda-mps-server
endif
endif

ifeq ($(BR2_PACKAGE_BATOCERA_NVIDIA_DRIVER_OPENCL),y)
BATOCERA_NVIDIA_DRIVER_LIBS += \
	libOpenCL.so.1.0.0 \
	libnvidia-opencl.so.$(BATOCERA_NVIDIA_DRIVER_VERSION)
BATOCERA_NVIDIA_DRIVER_DEPENDENCIES += mesa3d-headers
BATOCERA_NVIDIA_DRIVER_PROVIDES += libopencl
endif

# Build and install the kernel modules if needed
ifeq ($(BR2_PACKAGE_BATOCERA_NVIDIA_DRIVER_MODULE),y)

BATOCERA_NVIDIA_DRIVER_MODULES = nvidia nvidia-modeset nvidia-drm
ifeq ($(BR2_x86_64),y)
BATOCERA_NVIDIA_DRIVER_MODULES += nvidia-uvm
endif

# They can't do everything like everyone. They need those variables,
# because they don't recognise the usual variables set by the kernel
# build system. We also need to tell them what modules to build.
BATOCERA_NVIDIA_DRIVER_MODULE_MAKE_OPTS = \
	NV_KERNEL_SOURCES="$(LINUX_DIR)" \
	NV_KERNEL_OUTPUT="$(LINUX_DIR)" \
	NV_KERNEL_MODULES="$(BATOCERA_NVIDIA_DRIVER_MODULES)"

BATOCERA_NVIDIA_DRIVER_MODULE_SUBDIRS = kernel

$(eval $(kernel-module))

endif # BR2_PACKAGE_BATOCERA_NVIDIA_DRIVER_MODULE == y

# The downloaded archive is in fact an auto-extract script. So, it can run
# virtually everywhere, and it is fine enough to provide useful options.
# Except it can't extract into an existing (even empty) directory.
define BATOCERA_NVIDIA_DRIVER_EXTRACT_CMDS
	$(SHELL) $(BATOCERA_NVIDIA_DRIVER_DL_DIR)/$(BATOCERA_NVIDIA_DRIVER_SOURCE) --extract-only --target \
		$(@D)/tmp-extract
	chmod u+w -R $(@D)
	mv $(@D)/tmp-extract/* $(@D)/tmp-extract/.manifest $(@D)
	rm -rf $(@D)/tmp-extract
endef

# Helper to install libraries
# $1: destination directory (target or staging)
#
# For all libraries, we install them and create a symlink using
# their SONAME, so we can link to them at runtime; we also create
# the no-version symlink, so we can link to them at build time.
define BATOCERA_NVIDIA_DRIVER_INSTALL_LIBS
	$(foreach lib,$(BATOCERA_NVIDIA_DRIVER_LIBS),\
		$(INSTALL) -D -m 0644 $(@D)/$(lib) $(1)/usr/lib/$(notdir $(lib))
		libsoname="$$( $(TARGET_READELF) -d "$(@D)/$(lib)" \
			|sed -r -e '/.*\(SONAME\).*\[(.*)\]$$/!d; s//\1/;' )"; \
		if [ -n "$${libsoname}" -a "$${libsoname}" != "$(notdir $(lib))" ]; then \
			ln -sf $(notdir $(lib)) \
				$(1)/usr/lib/$${libsoname}; \
		fi
		baseso=$(firstword $(subst .,$(space),$(notdir $(lib)))).so; \
		if [ -n "$${baseso}" -a "$${baseso}" != "$(notdir $(lib))" ]; then \
			ln -sf $(notdir $(lib)) $(1)/usr/lib/$${baseso}; \
		fi
	)
endef

# batocera install 32bit libraries
define BATOCERA_NVIDIA_DRIVER_INSTALL_32
	$(foreach lib,$(BATOCERA_NVIDIA_DRIVER_32),\
		$(INSTALL) -D -m 0644 $(@D)/32/$(lib) $(1)/lib32/$(notdir $(lib))
		libsoname="$$( $(TARGET_READELF) -d "$(@D)/$(lib)" \
			|sed -r -e '/.*\(SONAME\).*\[(.*)\]$$/!d; s//\1/;' )"; \
		if [ -n "$${libsoname}" -a "$${libsoname}" != "$(notdir $(lib))" ]; then \
			ln -sf $(notdir $(lib)) \
				$(1)/lib32/$${libsoname}; \
		fi
		baseso=$(firstword $(subst .,$(space),$(notdir $(lib)))).so; \
		if [ -n "$${baseso}" -a "$${baseso}" != "$(notdir $(lib))" ]; then \
			ln -sf $(notdir $(lib)) $(1)/lib32/$${baseso}; \
		fi
	)
endef

# batocera nvidia libs are runtime linked via libglvnd
# For staging, install libraries and development files
# define BATOCERA_NVIDIA_DRIVER_INSTALL_STAGING_CMDS
# 	$(call BATOCERA_NVIDIA_DRIVER_INSTALL_LIBS,$(STAGING_DIR))
# 	$(BATOCERA_NVIDIA_DRIVER_INSTALL_GL_DEV)
# endef

# For target, install libraries and X.org modules
define BATOCERA_NVIDIA_DRIVER_INSTALL_TARGET_CMDS
	$(call BATOCERA_NVIDIA_DRIVER_INSTALL_LIBS,$(TARGET_DIR))
	$(call BATOCERA_NVIDIA_DRIVER_INSTALL_32,$(TARGET_DIR))
	$(foreach m,$(BATOCERA_NVIDIA_DRIVER_X_MODS), \
		$(INSTALL) -D -m 0644 $(@D)/$(notdir $(m)) \
			$(TARGET_DIR)/usr/lib/xorg/modules/$(m)
	)
	$(foreach p,$(BATOCERA_NVIDIA_DRIVER_PROGS), \
		$(INSTALL) -D -m 0755 $(@D)/$(p) \
			$(TARGET_DIR)/usr/bin/$(p)
	)
	$(BATOCERA_NVIDIA_DRIVER_INSTALL_KERNEL_MODULE)

# batocera install files needed by libglvnd
	$(INSTALL) -D -m 0644 $(@D)/10_nvidia.json \
		$(TARGET_DIR)/usr/share/glvnd/egl_vendor.d/10_nvidia.json

	$(INSTALL) -D -m 0644 $(@D)/nvidia-drm-outputclass.conf \
		$(TARGET_DIR)/usr/share/X11/xorg.conf.d/10-nvidia-drm-outputclass.conf

	$(INSTALL) -D -m 0644 $(@D)/libglxserver_nvidia.so.$(BATOCERA_NVIDIA_DRIVER_VERSION) \
	 	$(TARGET_DIR)/usr/lib/xorg/modules/extensions/libglxserver_nvidia.so.$(BATOCERA_NVIDIA_DRIVER_VERSION)
	ln -sf libglxserver_nvidia.so.$(BATOCERA_NVIDIA_DRIVER_VERSION) \
	 	$(TARGET_DIR)/usr/lib/xorg/modules/extensions/libglxserver_nvidia.so
	ln -sf libglxserver_nvidia.so.$(BATOCERA_NVIDIA_DRIVER_VERSION) \
	 	$(TARGET_DIR)/usr/lib/xorg/modules/extensions/libglxserver_nvidia.so.1

endef

$(eval $(generic-package))
