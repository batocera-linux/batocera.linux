################################################################################
#
# VULKAN_TOOLS
#
################################################################################

VULKAN_TOOLS_VERSION = 50e737c8234769be390c20b9adcb6408d32f6015
VULKAN_TOOLS_SITE =  https://github.com/KhronosGroup/Vulkan-Tools
VULKAN_TOOLS_SITE_METHOD=git
VULKAN_TOOLS_DEPENDENCIES = mesa3d vulkan-headers vulkan-loader
VULKAN_TOOLS_INSTALL_STAGING = YES
VULKAN_TOOLS_SUPPORTS_IN_SOURCE_BUILD = NO

VULKAN_TOOLS_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release -DVULKAN_HEADERS_INSTALL_DIR=$(STAGING_DIR)/usr/include/
VULKAN_TOOLS_CONF_ENV += LDFLAGS="--lpthread -ldl"

#define VULKAN_TOOLS_INSTALL_TARGET_CMDS
        #$(INSTALL) -D -m 0755 $(@D)/buildroot-build/third_party/lib/Release/x86_64/libktx.so $(TARGET_DIR)/usr/lib/libktx.so
        #$(INSTALL) -D -m 0755 $(@D)/buildroot-build/third_party/lib/Release/x86_64/libglslang-default-resource-limits.so $(TARGET_DIR)/usr/lib/libglslang-default-resource-limits.so
        #$(INSTALL) -D -m 0755 $(@D)/buildroot-build/third_party/lib/Release/x86_64/libastc.so $(TARGET_DIR)/usr/lib/libastc.so
        #$(INSTALL) -D -m 0755 $(@D)/buildroot-build/third_party/glfw/src/lib/Release/x86_64/libglfw.so.3.3 $(TARGET_DIR)/usr/lib/libglfw.so.3.3
        #$(INSTALL) -D -m 0755 $(@D)/buildroot-build/third_party/glfw/src/lib/Release/x86_64/libglfw.so.3 $(TARGET_DIR)/usr/lib/libglfw.so.3
        #$(INSTALL) -D -m 0755 $(@D)/buildroot-build/third_party/glfw/src/lib/Release/x86_64/libglfw.so $(TARGET_DIR)/usr/lib/libglfw.so
	#$(INSTALL) -D -m 0755 $(@D)/buildroot-build/app/bin/Release/x86_64/vulkan_TOOLS $(TARGET_DIR)/usr/bin/vulkan_TOOLS
#endef

$(eval $(cmake-package))
