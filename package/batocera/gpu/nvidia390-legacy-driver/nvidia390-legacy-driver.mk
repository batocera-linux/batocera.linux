################################################################################
#
# nvidia390-legacy-driver
#
################################################################################

NVIDIA390_LEGACY_DRIVER_VERSION = 390.157
NVIDIA390_LEGACY_DRIVER_SUFFIX = $(if $(BR2_x86_64),_64)
NVIDIA390_LEGACY_DRIVER_SITE = http://download.nvidia.com/XFree86/Linux-x86$(NVIDIA390_LEGACY_DRIVER_SUFFIX)/$(NVIDIA390_LEGACY_DRIVER_VERSION)
NVIDIA390_LEGACY_DRIVER_SOURCE = NVIDIA-Linux-x86$(NVIDIA390_LEGACY_DRIVER_SUFFIX)-$(NVIDIA390_LEGACY_DRIVER_VERSION).run
NVIDIA390_LEGACY_DRIVER_LICENSE = NVIDIA Software License
NVIDIA390_LEGACY_DRIVER_LICENSE_FILES = LICENSE
NVIDIA390_LEGACY_DRIVER_REDISTRIBUTE = NO
NVIDIA390_LEGACY_DRIVER_INSTALL_STAGING = YES

ifeq ($(BR2_PACKAGE_NVIDIA390_LEGACY_DRIVER_XORG),y)

# Since nvidia-driver are binary blobs, the below dependencies are not
# strictly speaking build dependencies of nvidia-driver. However, they
# are build dependencies of packages that depend on nvidia-driver, so
# they should be built prior to those packages, and the only simple
# way to do so is to make nvidia-driver depend on them.
#batocera enable nvidia-driver and mesa3d to coexist in the same fs
NVIDIA390_LEGACY_DRIVER_DEPENDENCIES = mesa3d xlib_libX11 xlib_libXext libglvnd kmod
# NVIDIA390_LEGACY_DRIVER_PROVIDES = libgl libegl libgles

# batocera modified to suport the vendor-neutral "dispatching" API/ABI
#   https://github.com/aritger/linux-opengl-abi-proposal/blob/master/linux-opengl-abi-proposal.txt
#batocera generic GL libraries are provided by libglvnd
#batocera only vendor version are installed
NVIDIA390_LEGACY_DRIVER_LIBS_GL = \
	libGLX_nvidia.so.$(NVIDIA390_LEGACY_DRIVER_VERSION)

NVIDIA390_LEGACY_DRIVER_LIBS_EGL = \
	libEGL_nvidia.so.$(NVIDIA390_LEGACY_DRIVER_VERSION)

NVIDIA390_LEGACY_DRIVER_LIBS_GLES = \
	libGLESv1_CM_nvidia.so.$(NVIDIA390_LEGACY_DRIVER_VERSION) \
	libGLESv2_nvidia.so.$(NVIDIA390_LEGACY_DRIVER_VERSION)

NVIDIA390_LEGACY_DRIVER_LIBS_MISC = \
	libnvidia-eglcore.so.$(NVIDIA390_LEGACY_DRIVER_VERSION) \
	libnvidia-glcore.so.$(NVIDIA390_LEGACY_DRIVER_VERSION) \
	libnvidia-glsi.so.$(NVIDIA390_LEGACY_DRIVER_VERSION) \
	tls/libnvidia-tls.so.$(NVIDIA390_LEGACY_DRIVER_VERSION) \
	libnvidia-ml.so.$(NVIDIA390_LEGACY_DRIVER_VERSION)

NVIDIA390_LEGACY_DRIVER_LIBS_VDPAU = \
	libvdpau_nvidia.so.$(NVIDIA390_LEGACY_DRIVER_VERSION)

NVIDIA390_LEGACY_DRIVER_LIBS += \
	$(NVIDIA390_LEGACY_DRIVER_LIBS_GL) \
	$(NVIDIA390_LEGACY_DRIVER_LIBS_EGL) \
	$(NVIDIA390_LEGACY_DRIVER_LIBS_GLES) \
	$(NVIDIA390_LEGACY_DRIVER_LIBS_MISC)

NVIDIA390_LEGACY_DRIVER_32 = \
	$(NVIDIA390_LEGACY_DRIVER_LIBS_GL) \
	$(NVIDIA390_LEGACY_DRIVER_LIBS_EGL) \
	$(NVIDIA390_LEGACY_DRIVER_LIBS_GLES) \
	libnvidia-eglcore.so.$(NVIDIA390_LEGACY_DRIVER_VERSION) \
	libnvidia-glcore.so.$(NVIDIA390_LEGACY_DRIVER_VERSION) \
	libnvidia-glsi.so.$(NVIDIA390_LEGACY_DRIVER_VERSION) \
	tls/libnvidia-tls.so.$(NVIDIA390_LEGACY_DRIVER_VERSION) \
	libnvidia-ml.so.$(NVIDIA390_LEGACY_DRIVER_VERSION)

# Install the gl.pc file
define NVIDIA390_LEGACY_DRIVER_INSTALL_GL_DEV
	$(INSTALL) -D -m 0644 $(@D)/libGL.la $(STAGING_DIR)/usr/lib/libGL.la
	$(SED) 's:__GENERATED_BY__:Buildroot:' $(STAGING_DIR)/usr/lib/libGL.la
	$(SED) 's:__LIBGL_PATH__:/usr/lib:' $(STAGING_DIR)/usr/lib/libGL.la
	$(SED) 's:-L[^[:space:]]\+::' $(STAGING_DIR)/usr/lib/libGL.la
	$(INSTALL) -D -m 0644 $(BR2_EXTERNAL_BATOCERA_PATH)/package/nvidia-driver/gl.pc $(STAGING_DIR)/usr/lib/pkgconfig/gl.pc
	$(INSTALL) -D -m 0644 $(BR2_EXTERNAL_BATOCERA_PATH)/package/nvidia-driver/egl.pc $(STAGING_DIR)/usr/lib/pkgconfig/egl.pc
endef
endif # X drivers

# Build and install the kernel modules if needed
ifeq ($(BR2_PACKAGE_NVIDIA390_LEGACY_DRIVER_MODULE),y)
NVIDIA390_LEGACY_DRIVER_MODULES = nvidia nvidia-modeset nvidia-drm
ifeq ($(BR2_x86_64),y)
NVIDIA390_LEGACY_DRIVER_MODULES += nvidia-uvm
endif

# They can't do everything like everyone. They need those variables,
# because they don't recognise the usual variables set by the kernel
# build system. We also need to tell them what modules to build.
NVIDIA390_LEGACY_DRIVER_MODULE_MAKE_OPTS = \
	NV_KERNEL_SOURCES="$(LINUX_DIR)" \
	NV_KERNEL_OUTPUT="$(LINUX_DIR)" \
	NV_KERNEL_MODULES="$(NVIDIA390_LEGACY_DRIVER_MODULES)" \
	IGNORE_CC_MISMATCH="1" \
	NV_SPECTRE_V2="0"

NVIDIA390_LEGACY_DRIVER_MODULE_SUBDIRS = kernel

$(eval $(kernel-module))

endif # BR2_PACKAGE_NVIDIA390_LEGACY_DRIVER_MODULE == y

# The downloaded archive is in fact an auto-extract script. So, it can run
# virtually everywhere, and it is fine enough to provide useful options.
# Except it can't extract into an existing (even empty) directory.
define NVIDIA390_LEGACY_DRIVER_EXTRACT_CMDS
	$(SHELL) $(NVIDIA390_LEGACY_DRIVER_DL_DIR)/$(NVIDIA390_LEGACY_DRIVER_SOURCE) --extract-only --target \
		$(@D)/tmp-extract
	chmod u+w -R $(@D)
	mv $(@D)/tmp-extract/* $(@D)/tmp-extract/.manifest $(@D)
	rm -rf $(@D)/tmp-extract
endef

# Helper to install libraries
# $1: destination directory (target or staging)
define NVIDIA390_LEGACY_DRIVER_INSTALL_LIBS
	$(foreach lib,$(NVIDIA390_LEGACY_DRIVER_LIBS),\
		$(INSTALL) -D -m 0644 $(@D)/$(lib) $(1)/usr/lib/$(notdir $(lib))
	)
	$(foreach lib,$(NVIDIA390_LEGACY_DRIVER_LIBS_VDPAU),\
		$(INSTALL) -D -m 0644 $(@D)/$(lib) $(1)/usr/lib/vdpau/$(notdir $(lib))
	)
endef

# batocera install 32bit libraries
define NVIDIA390_LEGACY_DRIVER_INSTALL_32
	$(foreach lib,$(NVIDIA390_LEGACY_DRIVER_32),\
		$(INSTALL) -D -m 0644 $(@D)/32/$(lib) $(1)/lib32/$(notdir $(lib))
	)
	$(foreach lib,$(NVIDIA390_LEGACY_DRIVER_LIBS_VDPAU),\
		$(INSTALL) -D -m 0644 $(@D)/32/$(lib) $(1)/lib32/vdpau/$(notdir $(lib))
	)
endef

# For target, install libraries and X.org modules
define NVIDIA390_LEGACY_DRIVER_INSTALL_TARGET_CMDS
	$(call NVIDIA390_LEGACY_DRIVER_INSTALL_LIBS,$(TARGET_DIR))
	$(call NVIDIA390_LEGACY_DRIVER_INSTALL_32,$(TARGET_DIR))
	$(INSTALL) -D -m 0644 $(@D)/nvidia_drv.so \
			$(TARGET_DIR)/usr/lib/xorg/modules/drivers/nvidia390_legacy_drv.so
	$(INSTALL) -D -m 0644 $(@D)/libglx.so.$(NVIDIA390_LEGACY_DRIVER_VERSION) \
	        $(TARGET_DIR)/usr/lib/xorg/modules/extensions/libglx.so.$(NVIDIA390_LEGACY_DRIVER_VERSION)
	$(NVIDIA390_LEGACY_DRIVER_INSTALL_KERNEL_MODULE)
	
	# batocera install files needed by libglvnd
	$(INSTALL) -D -m 0644 $(@D)/10_nvidia.json \
		$(TARGET_DIR)/usr/share/glvnd/egl_vendor.d/10_nvidia390_legacy.json

	mkdir -p $(TARGET_DIR)/usr/share/nvidia
	mkdir -p $(TARGET_DIR)/usr/share/nvidia/X11
	$(INSTALL) -D -m 0644 $(@D)/nvidia-drm-outputclass.conf \
		$(TARGET_DIR)/usr/share/nvidia/X11/10-nvidia390-legacy-drm-outputclass.conf
endef

# move to avoid the production driver
define NVIDIA390_LEGACY_DRIVER_RENAME_KERNEL_MODULES
    mkdir -p $(TARGET_DIR)/usr/share/nvidia
	mkdir -p $(TARGET_DIR)/usr/share/nvidia/modules
	mkdir -p $(TARGET_DIR)/usr/share/nvidia/xorg/
    # rename the kernel modules to avoid conflict
	mv -f $(TARGET_DIR)/lib/modules/$(LINUX_VERSION_PROBED)/updates/nvidia.ko \
	    $(TARGET_DIR)/usr/share/nvidia/modules/nvidia390-legacy.ko
	mv -f $(TARGET_DIR)/lib/modules/$(LINUX_VERSION_PROBED)/updates/nvidia-modeset.ko \
	    $(TARGET_DIR)/usr/share/nvidia/modules/nvidia390-modeset-legacy.ko
	mv -f $(TARGET_DIR)/lib/modules/$(LINUX_VERSION_PROBED)/updates/nvidia-drm.ko \
	    $(TARGET_DIR)/usr/share/nvidia/modules/nvidia390-drm-legacy.ko	
	mv -f $(TARGET_DIR)/lib/modules/$(LINUX_VERSION_PROBED)/updates/nvidia-uvm.ko \
	    $(TARGET_DIR)/usr/share/nvidia/modules/nvidia390-uvm-legacy.ko
	mv -f $(TARGET_DIR)/usr/lib/xorg/modules/extensions/libglx.so.$(NVIDIA390_LEGACY_DRIVER_VERSION) \
	    $(TARGET_DIR)/usr/share/nvidia/xorg/libglx.so.$(NVIDIA390_LEGACY_DRIVER_VERSION)
	# set the driver version file
	echo $(NVIDIA390_LEGACY_DRIVER_VERSION) > $(TARGET_DIR)/usr/share/nvidia/legacy390.version
endef

NVIDIA390_LEGACY_DRIVER_POST_INSTALL_TARGET_HOOKS += NVIDIA390_LEGACY_DRIVER_RENAME_KERNEL_MODULES

$(eval $(generic-package))
