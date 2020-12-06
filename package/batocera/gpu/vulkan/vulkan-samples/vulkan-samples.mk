################################################################################
#
# VULKAN_SAMPLES
#
################################################################################

VULKAN_SAMPLES_VERSION = f52361d3cd6ac8c30fc3365a464b4e220c32cfd6
VULKAN_SAMPLES_SITE =  https://github.com/KhronosGroup/Vulkan-Samples
VULKAN_SAMPLES_GIT_SUBMODULES=YES
VULKAN_SAMPLES_SITE_METHOD=git
VULKAN_SAMPLES_DEPENDENCIES = mesa3d vulkan-headers vulkan-loader
VULKAN_SAMPLES_INSTALL_STAGING = YES
VULKAN_SAMPLES_SUPPORTS_IN_SOURCE_BUILD = NO

VULKAN_SAMPLES_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release
VULKAN_SAMPLES_CONF_OPTS += -DBUILD_SHARED_LIBS=OFF
VULKAN_SAMPLES_CONF_ENV += LDFLAGS="--lpthread -ldl"

# Terrible temporary workaround for rpi4
VULKAN_SAMPLES_INSTALL_ARCH = $(BR2_ARCH)
ifeq ($(ARCH),arm)
VULKAN_SAMPLES_INSTALL_ARCH = armv8l
endif

define VULKAN_SAMPLES_INSTALL_TARGET_CMDS
	$(INSTALL) -D -m 0755 $(@D)/buildroot-build/app/bin/Release/$(VULKAN_SAMPLES_INSTALL_ARCH)/vulkan_samples $(TARGET_DIR)/usr/bin/vulkan_samples
endef

$(eval $(cmake-package))
