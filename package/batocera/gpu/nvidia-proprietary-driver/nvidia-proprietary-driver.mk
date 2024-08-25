################################################################################
#
# nvidia-proprietary-driver
#
################################################################################

NVIDIA_PROPRIETARY_DRIVER_VERSION = $(NVIDIA_OPEN_DRIVER_VERSION)
NVIDIA_PROPRIETARY_DRIVER_SUFFIX = $(if $(BR2_x86_64),_64)
NVIDIA_PROPRIETARY_DRIVER_SITE = \
    http://download.nvidia.com/XFree86/Linux-x86$(NVIDIA_PROPRIETARY_DRIVER_SUFFIX)/$(NVIDIA_PROPRIETARY_DRIVER_VERSION)
NVIDIA_PROPRIETARY_DRIVER_SOURCE = \
    NVIDIA-Linux-x86$(NVIDIA_PROPRIETARY_DRIVER_SUFFIX)-$(NVIDIA_PROPRIETARY_DRIVER_VERSION).run
NVIDIA_PROPRIETARY_DRIVER_LICENSE = NVIDIA Software License
NVIDIA_PROPRIETARY_DRIVER_LICENSE_FILES = LICENSE
NVIDIA_PROPRIETARY_DRIVER_REDISTRIBUTE = NO

# Build and install the proprietary kernel modules if needed
ifeq ($(BR2_PACKAGE_NVIDIA_PROPRIETARY_DRIVER_MODULE),y)

NVIDIA_PROPRIETARY_DRIVER_MODULES = nvidia nvidia-modeset nvidia-drm
ifeq ($(BR2_x86_64),y)
NVIDIA_PROPRIETARY_DRIVER_MODULES += nvidia-uvm
endif

# They can't do everything like everyone. They need those variables,
# because they don't recognise the usual variables set by the kernel
# build system. We also need to tell them what modules to build.
NVIDIA_PROPRIETARY_DRIVER_MODULE_MAKE_OPTS = \
	NV_KERNEL_SOURCES="$(LINUX_DIR)" \
	NV_KERNEL_OUTPUT="$(LINUX_DIR)" \
	NV_KERNEL_MODULES="$(NVIDIA_PROPRIETARY_DRIVER_MODULES)" \
	IGNORE_CC_MISMATCH="1"

NVIDIA_PROPRIETARY_DRIVER_MODULE_SUBDIRS = kernel

$(eval $(kernel-module))

endif # BR2_PACKAGE_NVIDIA_PROPRIETARY_DRIVER_MODULE == y

# The downloaded archive is in fact an auto-extract script. So, it can run
# virtually everywhere, and it is fine enough to provide useful options.
# Except it can't extract into an existing (even empty) directory.
define NVIDIA_PROPRIETARY_DRIVER_EXTRACT_CMDS
	$(SHELL) $(NVIDIA_PROPRIETARY_DRIVER_DL_DIR)/$(NVIDIA_PROPRIETARY_DRIVER_SOURCE) --extract-only --target \
		$(@D)/tmp-extract
	chmod u+w -R $(@D)
	mv $(@D)/tmp-extract/* $(@D)/tmp-extract/.manifest $(@D)
	rm -rf $(@D)/tmp-extract
endef

KVER = $(shell expr $(BR2_LINUX_KERNEL_CUSTOM_VERSION_VALUE))

# keep a copy of the proprietary driver for legacy -> proprietary migrations
define NVIDIA_PROPRIETARY_DRIVER_RENAME_KERNEL_MODULES
	mkdir -p $(TARGET_DIR)/usr/share/nvidia
	mkdir -p $(TARGET_DIR)/usr/share/nvidia/modules
    # rename the kernel modules to avoid conflict
	mv -f $(TARGET_DIR)/lib/modules/$(LINUX_VERSION_PROBED)/updates/nvidia.ko \
	    $(TARGET_DIR)/usr/share/nvidia/modules/nvidia-proprietary.ko
	mv -f $(TARGET_DIR)/lib/modules/$(LINUX_VERSION_PROBED)/updates/nvidia-modeset.ko \
	    $(TARGET_DIR)/usr/share/nvidia/modules/nvidia-modeset-proprietary.ko
	mv -f $(TARGET_DIR)/lib/modules/$(LINUX_VERSION_PROBED)/updates/nvidia-drm.ko \
	    $(TARGET_DIR)/usr/share/nvidia/modules/nvidia-drm-proprietary.ko	
	mv -f $(TARGET_DIR)/lib/modules/$(LINUX_VERSION_PROBED)/updates/nvidia-uvm.ko \
	    $(TARGET_DIR)/usr/share/nvidia/modules/nvidia-uvm-proprietary.ko
endef

NVIDIA_PROPRIETARY_DRIVER_POST_INSTALL_TARGET_HOOKS += NVIDIA_PROPRIETARY_DRIVER_RENAME_KERNEL_MODULES

$(eval $(generic-package))
