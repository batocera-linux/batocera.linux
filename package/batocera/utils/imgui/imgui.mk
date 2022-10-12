################################################################################
#
# imgui
#
################################################################################

IMGUI_VERSION = v1.88
IMGUI_SITE = $(call github,ocornut,imgui,$(IMGUI_VERSION))

IMGUI_CONF_OPTS = -DCMAKE_BUILD_TYPE=Release
HOST_IMGUI_CONF_OPTS = -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX=$(STAGING_DIR)/usr

ifeq ($(BR2_PACKAGE_LIBGLFW),y)
    HOST_IMGUI_DEPENDENCIES += libglfw
    HOST_IMGUI_CONF_OPTS += -DIMGUI_BUILD_GLFW_BINDING=ON
endif

ifeq ($(BR2_PACKAGE_LIBFREEGLUT),y)
    HOST_IMGUI_DEPENDENCIES += libfreeglut
    HOST_IMGUI_CONF_OPTS += -DIMGUI_BUILD_GLUT_BINDING=ON
endif

ifeq ($(BR2_PACKAGE_BATOCERA_GLES2),y)
    HOST_IMGUI_DEPENDENCIES += libgles
    HOST_IMGUI_CONF_OPTS += -DIMGUI_BUILD_OPENGL2_BINDING=ON
endif

ifeq ($(BR2_PACKAGE_BATOCERA_GLES3),y)
    HOST_IMGUI_DEPENDENCIES += libgles
    HOST_IMGUI_CONF_OPTS += -DIMGUI_BUILD_OPENGL3_BINDING=ON
endif

ifeq ($(BR2_PACKAGE_SDL2),y)
    HOST_IMGUI_DEPENDENCIES += sdl2
    HOST_IMGUI_CONF_OPTS += -DIMGUI_BUILD_SDL2_BINDING=ON -DIMGUI_BUILD_SDL2_RENDERER_BINDING=ON
endif

ifeq ($(BR2_PACKAGE_VULKAN_LOADER),y)
    IHOST_MGUI_DEPENDENCIES += vulkan-headers vulkan-loader
    HOST_IMGUI_CONF_OPTS += -DIMGUI_BUILD_VULKAN_BINDING=ON
endif

define IMGUI_COPY_CMAKE_FILES
    cp -f $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/utils/imgui/CMakeLists.txt \
	  $(@D)/
    cp -f $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/utils/imgui/imgui-config.cmake.in \
	  $(@D)/
endef

IMGUI_PRE_CONFIGURE_HOOKS += IMGUI_COPY_CMAKE_FILES
HOST_IMGUI_PRE_CONFIGURE_HOOKS += IMGUI_COPY_CMAKE_FILES

$(eval $(cmake-package))
$(eval $(host-cmake-package))
