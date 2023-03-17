################################################################################
#
# batocera-nvidia-driver
#
################################################################################

BATOCERA_NVIDIA_DRIVER_VERSION = 525.89.02
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
BATOCERA_NVIDIA_DRIVER_DEPENDENCIES = mesa3d xlib_libX11 xlib_libXext libglvnd \
    batocera-nvidia-legacy-driver batocera-nvidia390-legacy-driver batocera-nvidia340-legacy-driver

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
	libnvidia-egl-wayland.so.1.1.10 \
	libnvidia-glcore.so.$(BATOCERA_NVIDIA_DRIVER_VERSION) \
	libnvidia-glsi.so.$(BATOCERA_NVIDIA_DRIVER_VERSION) \
	libnvidia-tls.so.$(BATOCERA_NVIDIA_DRIVER_VERSION) \
	libvdpau_nvidia.so.$(BATOCERA_NVIDIA_DRIVER_VERSION) \
	libnvidia-ml.so.$(BATOCERA_NVIDIA_DRIVER_VERSION) \
	libnvidia-glvkspirv.so.$(BATOCERA_NVIDIA_DRIVER_VERSION)

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
	libnvidia-ml.so.$(BATOCERA_NVIDIA_DRIVER_VERSION) \
	libnvidia-glvkspirv.so.$(BATOCERA_NVIDIA_DRIVER_VERSION)

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
	NV_KERNEL_MODULES="$(BATOCERA_NVIDIA_DRIVER_MODULES)" \
	IGNORE_CC_MISMATCH="1"


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
	$(INSTALL) -D -m 0644 $(@D)/nvidia_drv.so \
			$(TARGET_DIR)/usr/lib/xorg/modules/drivers/nvidia_production_drv.so
	$(foreach p,$(BATOCERA_NVIDIA_DRIVER_PROGS), \
		$(INSTALL) -D -m 0755 $(@D)/$(p) \
			$(TARGET_DIR)/usr/bin/$(p)
	)
	$(BATOCERA_NVIDIA_DRIVER_INSTALL_KERNEL_MODULE)

# install nvidia-modprobe, required
	$(INSTALL) -D -m 0755 $(@D)/nvidia-modprobe $(TARGET_DIR)/usr/bin/nvidia-modprobe

# batocera install files needed by Vulkan
	$(INSTALL) -D -m 0644 $(@D)/nvidia_layers.json \
		$(TARGET_DIR)/usr/share/vulkan/implicit_layer.d/nvidia_production_layers.json

# batocera install files needed by libglvnd
	$(INSTALL) -D -m 0644 $(@D)/10_nvidia.json \
		$(TARGET_DIR)/usr/share/glvnd/egl_vendor.d/10_nvidia_production.json

	$(INSTALL) -D -m 0644 $(@D)/nvidia-drm-outputclass.conf \
		$(TARGET_DIR)/usr/share/X11/xorg.conf.d/10-nvidia-production-drm-outputclass.conf

	$(INSTALL) -D -m 0644 $(@D)/libglxserver_nvidia.so.$(BATOCERA_NVIDIA_DRIVER_VERSION) \
	 	$(TARGET_DIR)/usr/lib/xorg/modules/extensions/libglxserver_nvidia.so.$(BATOCERA_NVIDIA_DRIVER_VERSION)
	ln -sf libglxserver_nvidia.so.$(BATOCERA_NVIDIA_DRIVER_VERSION) \
	 	$(TARGET_DIR)/usr/lib/xorg/modules/extensions/libglxserver_nvidia.so
	ln -sf libglxserver_nvidia.so.$(BATOCERA_NVIDIA_DRIVER_VERSION) \
	 	$(TARGET_DIR)/usr/lib/xorg/modules/extensions/libglxserver_nvidia.so.1

endef

define BATOCERA_NVIDIA_DRIVER_VULKANJSON_X86_64
    mkdir -p $(TARGET_DIR)/usr/share/vulkan/nvidia
	$(INSTALL) -D -m 0644 $(@D)/nvidia_icd.json $(TARGET_DIR)/usr/share/vulkan/nvidia/nvidia_production_icd.x86_64.json
        sed -i -e s+'"library_path": "libGLX_nvidia'+'"library_path": "/usr/lib/libGLX_nvidia'+ $(TARGET_DIR)/usr/share/vulkan/nvidia/nvidia_production_icd.x86_64.json
	$(INSTALL) -D -m 0644 $(@D)/nvidia_icd.json $(TARGET_DIR)/usr/share/vulkan/nvidia/nvidia_production_icd.i686.json
        sed -i -e s+'"library_path": "libGLX_nvidia'+'"library_path": "/lib32/libGLX_nvidia'+ $(TARGET_DIR)/usr/share/vulkan/nvidia/nvidia_production_icd.i686.json
endef

define BATOCERA_NVIDIA_DRIVER_VULKANJSON_X86
    mkdir -p $(TARGET_DIR)/usr/share/vulkan/nvidia
	$(INSTALL) -D -m 0644 $(@D)/nvidia_icd.json $(TARGET_DIR)/usr/share/vulkan/nvidia/nvidia_production_icd.i686.json
endef

ifeq ($(BR2_x86_64),y)
	BATOCERA_NVIDIA_DRIVER_POST_INSTALL_TARGET_HOOKS += BATOCERA_NVIDIA_DRIVER_VULKANJSON_X86_64
endif
ifeq ($(BR2_i686),y)
	BATOCERA_NVIDIA_DRIVER_POST_INSTALL_TARGET_HOOKS += BATOCERA_NVIDIA_DRIVER_VULKANJSON_X86
endif

KVER = $(shell expr $(BR2_LINUX_KERNEL_CUSTOM_VERSION_VALUE))

# keep a copy of the production driver for legacy - production migrations
define BATOCERA_NVIDIA_DRIVER_RENAME_KERNEL_MODULES
	mkdir -p $(TARGET_DIR)/usr/share/nvidia
	mkdir -p $(TARGET_DIR)/usr/share/nvidia/modules
    # rename the kernel modules to avoid conflict
	cp $(TARGET_DIR)/lib/modules/$(LINUX_VERSION_PROBED)/extra/nvidia.ko \
	    $(TARGET_DIR)/usr/share/nvidia/modules/nvidia-production.ko
	cp $(TARGET_DIR)/lib/modules/$(LINUX_VERSION_PROBED)/extra/nvidia-modeset.ko \
	    $(TARGET_DIR)/usr/share/nvidia/modules/nvidia-modeset-production.ko
	cp $(TARGET_DIR)/lib/modules/$(LINUX_VERSION_PROBED)/extra/nvidia-drm.ko \
	    $(TARGET_DIR)/usr/share/nvidia/modules/nvidia-drm-production.ko	
	cp $(TARGET_DIR)/lib/modules/$(LINUX_VERSION_PROBED)/extra/nvidia-uvm.ko \
	    $(TARGET_DIR)/usr/share/nvidia/modules/nvidia-uvm-production.ko
	# set the driver version file
	echo $(BATOCERA_NVIDIA_DRIVER_VERSION) > $(TARGET_DIR)/usr/share/nvidia/production.version
endef

BATOCERA_NVIDIA_DRIVER_POST_INSTALL_TARGET_HOOKS += BATOCERA_NVIDIA_DRIVER_RENAME_KERNEL_MODULES

$(eval $(generic-package))
