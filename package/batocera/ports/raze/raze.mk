################################################################################
#
# raze
#
################################################################################

RAZE_VERSION = 1.10.2
RAZE_SITE = $(call github,coelckers,Raze,$(RAZE_VERSION))
RAZE_LICENSE = GPLv2
RAZE_DEPENDENCIES = host-raze sdl2 bzip2 fluidsynth openal zmusic webp
RAZE_SUPPORTS_IN_SOURCE_BUILD = NO

# We need the tools from the host package to build the target package
HOST_RAZE_DEPENDENCIES = zlib bzip2 host-webp
HOST_RAZE_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release
HOST_RAZE_CONF_OPTS += -DSKIP_INSTALL_ALL=ON

# The TOOLS_ONLY=ON option is not implemented in Raze yet.
# This does in fact build the entire engine, not just the build tools.
# We disable Vulkan to avoid having to depend on `host-xlib_libX11`.
HOST_RAZE_CONF_OPTS += -DTOOLS_ONLY=ON
HOST_RAZE_CONF_OPTS += -DHAVE_VULKAN=OFF
HOST_RAZE_SUPPORTS_IN_SOURCE_BUILD = NO

define HOST_RAZE_INSTALL_CMDS
	# Skip install as we only need `ImportExecutables.cmake` from the build directory.
endef

RAZE_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release
RAZE_CONF_OPTS += -DFORCE_CROSSCOMPILE=ON
RAZE_CONF_OPTS += -DBUILD_SHARED_LIBS=OFF
RAZE_CONF_OPTS += -DIMPORT_EXECUTABLES="$(HOST_RAZE_BUILDDIR)/ImportExecutables.cmake"

ifeq ($(BR2_PACKAGE_BATOCERA_VULKAN),y)
    ifeq ($(BR2_PACKAGE_XSERVER_XORG_SERVER),y)
        RAZE_DEPENDENCIES += xlib_libX11 vulkan-headers vulkan-loader
        RAZE_CONF_OPTS += -DHAVE_VULKAN=ON
        RAZE_CONF_OPTS += -DVULKAN_USE_XLIB=ON -DVULKAN_USE_WAYLAND=OFF
    else ifeq ($(BR2_PACKAGE_BATOCERA_WAYLAND_SWAY),y)
        RAZE_DEPENDENCIES += wayland vulkan-headers vulkan-loader
        RAZE_CONF_OPTS += -DHAVE_VULKAN=ON
        RAZE_CONF_OPTS += -DVULKAN_USE_XLIB=OFF -DVULKAN_USE_WAYLAND=ON
    else
        # no valid surface provider
        RAZE_CONF_OPTS += -DHAVE_VULKAN=OFF
    endif
else
    RAZE_CONF_OPTS += -DHAVE_VULKAN=OFF
endif

ifeq ($(BR2_PACKAGE_BATOCERA_GLES3)$(BR2_PACKAGE_BATOCERA_GLES2),y)
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
