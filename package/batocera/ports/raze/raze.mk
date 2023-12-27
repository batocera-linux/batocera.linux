################################################################################
#
# raze
#
################################################################################

RAZE_VERSION = 1.8.1
RAZE_SITE = $(call github,coelckers,Raze,$(RAZE_VERSION))
RAZE_LICENSE = GPLv2
RAZE_DEPENDENCIES = host-raze sdl2 bzip2 fluidsynth openal zmusic
RAZE_SUPPORTS_IN_SOURCE_BUILD = NO

# We need the tools from the host package to build the target package
HOST_RAZE_DEPENDENCIES = zlib bzip2
HOST_RAZE_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release
HOST_RAZE_CONF_OPTS += -DSKIP_INSTALL_ALL=ON
HOST_RAZE_CONF_OPTS += -DTOOLS_ONLY=ON
HOST_RAZE_SUPPORTS_IN_SOURCE_BUILD = NO

define HOST_RAZE_INSTALL_CMDS
	# Skip install as we only need `ImportExecutables.cmake` from the build directory.
endef

RAZE_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release
RAZE_CONF_OPTS += -DFORCE_CROSSCOMPILE=ON
RAZE_CONF_OPTS += -DBUILD_SHARED_LIBS=OFF
RAZE_CONF_OPTS += -DIMPORT_EXECUTABLES="$(HOST_RAZE_BUILDDIR)/ImportExecutables.cmake"

# ZVulkan has X11 or Waylan options now
ifeq ($(BR2_PACKAGE_VULKAN_HEADERS)$(BR2_PACKAGE_VULKAN_LOADER),yy)
    ifeq ($(BR2_PACKAGE_XORG7),y)
        RAZE_CONF_OPTS += -DHAVE_VULKAN=ON
        RAZE_CONF_OPTS += -DVULKAN_USE_XLIB=ON
        RAZE_CONF_OPTS += -DVULKAN_USE_WAYLAND=OFF
        HOST_RAZE_CONF_OPTS += -DHAVE_VULKAN=ON
        HOST_RAZE_CONF_OPTS += -DVULKAN_USE_XLIB=ON
        HOST_RAZE_CONF_OPTS += -DVULKAN_USE_WAYLAND=OFF
        RAZE_DEPENDENCIES += vulkan-headers vulkan-loader
    else ifeq ($(BR2_PACKAGE_WAYLAND),y)
        RAZE_CONF_OPTS += -DHAVE_VULKAN=ON
        RAZE_CONF_OPTS += -DVULKAN_USE_XLIB=OFF
        RAZE_CONF_OPTS += -DVULKAN_USE_WAYLAND=ON
        HOST_RAZE_CONF_OPTS += -DHAVE_VULKAN=ON
        HOST_RAZE_CONF_OPTS += -DVULKAN_USE_XLIB=OFF
        HOST_RAZE_CONF_OPTS += -DVULKAN_USE_WAYLAND=ON
        RAZE_DEPENDENCIES += vulkan-headers vulkan-loader
    else
        RAZE_CONF_OPTS += -DHAVE_VULKAN=OFF
        HOST_RAZE_CONF_OPTS += -DHAVE_VULKAN=OFF
    endif
else
    RAZE_CONF_OPTS += -DHAVE_VULKAN=OFF
    HOST_RAZE_CONF_OPTS += -DHAVE_VULKAN=OFF
endif

ifeq ($(BR2_PACKAGE_BATOCERA_GLES3),y)
    RAZE_CONF_OPTS += -DHAVE_GLES2=ON
    RAZE_DEPENDENCIES += libgles
else ifeq ($(BR2_PACKAGE_BATOCERA_GLES2),y)
    RAZE_CONF_OPTS += -DHAVE_GLES2=ON
    RAZE_DEPENDENCIES += libgles
else
    RAZE_CONF_OPTS += -DHAVE_GLES2=OFF
    RAZE_DEPENDENCIES += libgl
endif

define RAZE_INSTALL_TARGET_CMDS
    $(INSTALL) -D -m 0755 $(@D)/buildroot-build/raze \
        $(TARGET_DIR)/usr/bin/raze
    $(INSTALL) -D -m 0755 $(@D)/buildroot-build/raze.pk3 \
        $(TARGET_DIR)/usr/share/raze/raze.pk3
    $(INSTALL) -D -m 0755 $(@D)/buildroot-build/soundfonts/raze.sf2 \
        $(TARGET_DIR)/usr/share/raze/soundfonts/raze.sf2
    mkdir -p $(TARGET_DIR)/usr/share/evmapy
    cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/ports/raze/raze.keys \
        $(TARGET_DIR)/usr/share/evmapy
endef

$(eval $(cmake-package))
$(eval $(host-cmake-package))
