################################################################################
#
# VULKAN_SAMPLES
#
################################################################################

VULKAN_SAMPLES_VERSION = 6c04bbd5baa9a7652fb35e86cf859c2b29a929f2
VULKAN_SAMPLES_SITE =  https://github.com/KhronosGroup/Vulkan-Samples
VULKAN_SAMPLES_GIT_SUBMODULES=YES
VULKAN_SAMPLES_SITE_METHOD=git
VULKAN_SAMPLES_DEPENDENCIES = mesa3d vulkan-headers vulkan-loader
VULKAN_SAMPLES_INSTALL_STAGING = YES
VULKAN_SAMPLES_SUPPORTS_IN_SOURCE_BUILD = NO

VULKAN_SAMPLES_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release
VULKAN_SAMPLES_CONF_ENV += LDFLAGS="--lpthread -ldl"

define VULKAN_SAMPLES_INSTALL_TARGET_CMDS
        $(INSTALL) -D -m 0755 $(@D)/buildroot-build/third_party/lib/Release/x86_64/libktx.so $(TARGET_DIR)/usr/lib/libktx.so
        $(INSTALL) -D -m 0755 $(@D)/buildroot-build/third_party/lib/Release/x86_64/libglslang-default-resource-limits.so $(TARGET_DIR)/usr/lib/libglslang-default-resource-limits.so
        $(INSTALL) -D -m 0755 $(@D)/buildroot-build/third_party/lib/Release/x86_64/libastc.so $(TARGET_DIR)/usr/lib/libastc.so
        $(INSTALL) -D -m 0755 $(@D)/buildroot-build/third_party/glfw/src/lib/Release/x86_64/libglfw.so.3.3 $(TARGET_DIR)/usr/lib/libglfw.so.3.3
        $(INSTALL) -D -m 0755 $(@D)/buildroot-build/third_party/glfw/src/lib/Release/x86_64/libglfw.so.3 $(TARGET_DIR)/usr/lib/libglfw.so.3
        $(INSTALL) -D -m 0755 $(@D)/buildroot-build/third_party/glfw/src/lib/Release/x86_64/libglfw.so $(TARGET_DIR)/usr/lib/libglfw.so
	$(INSTALL) -D -m 0755 $(@D)/buildroot-build/app/bin/Release/x86_64/vulkan_samples $(TARGET_DIR)/usr/bin/vulkan_samples
endef

$(eval $(cmake-package))
