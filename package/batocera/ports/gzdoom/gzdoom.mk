################################################################################
#
# gzdoom
#
################################################################################

GZDOOM_VERSION = g4.14.2
GZDOOM_HASH = 99aa489 # get from the tag
GZDOOM_SITE = https://github.com/ZDoom/gzdoom.git
GZDOOM_SITE_METHOD = git
GZDOOM_GIT_SUBMODULES = YES
GZDOOM_LICENSE = GPLv3
GZDOOM_DEPENDENCIES = host-gzdoom sdl2 bzip2 fluidsynth openal zmusic libvpx webp
GZDOOM_SUPPORTS_IN_SOURCE_BUILD = NO
GZDOOM_EMULATOR_INFO = gzdoom.emulator.yml

# We need the tools from the host package to build the target package
HOST_GZDOOM_DEPENDENCIES = zlib bzip2 host-webp
HOST_GZDOOM_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release
HOST_GZDOOM_CONF_OPTS += -DSKIP_INSTALL_ALL=ON
HOST_GZDOOM_CONF_OPTS += -DTOOLS_ONLY=ON
HOST_GZDOOM_SUPPORTS_IN_SOURCE_BUILD = NO

define HOST_GZDOOM_INSTALL_CMDS
	# Skip install as we only need `ImportExecutables.cmake` from the build directory.
endef

GZDOOM_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release
GZDOOM_CONF_OPTS += -DFORCE_CROSSCOMPILE=ON
GZDOOM_CONF_OPTS += -DBUILD_SHARED_LIBS=OFF
GZDOOM_CONF_OPTS += -DNO_SDL_JOYSTICK=OFF
GZDOOM_CONF_OPTS += -DIMPORT_EXECUTABLES="$(HOST_GZDOOM_BUILDDIR)/ImportExecutables.cmake"

ifeq ($(BR2_PACKAGE_BATOCERA_VULKAN),y)
    ifeq ($(BR2_PACKAGE_XSERVER_XORG_SERVER),y)
        GZDOOM_DEPENDENCIES += xlib_libX11 vulkan-headers vulkan-loader
        GZDOOM_CONF_OPTS += -DHAVE_VULKAN=ON
        GZDOOM_CONF_OPTS += -DVULKAN_USE_XLIB=ON -DVULKAN_USE_WAYLAND=OFF
    else ifeq ($(BR2_PACKAGE_WAYLAND),y)
        GZDOOM_DEPENDENCIES += wayland vulkan-headers vulkan-loader
        GZDOOM_CONF_OPTS += -DHAVE_VULKAN=ON
        GZDOOM_CONF_OPTS += -DVULKAN_USE_XLIB=OFF -DVULKAN_USE_WAYLAND=ON
    else
        # no valid surface provider
        GZDOOM_CONF_OPTS += -DHAVE_VULKAN=OFF
    endif
else
    GZDOOM_CONF_OPTS += -DHAVE_VULKAN=OFF
endif

# This applies the patches to actually use GLES2.
# By default, gzdoom attempts to use GLES2 with an OpenGL context.
# This only works if the system has both OpenGL and GLES2.
#
# To fix this, we need to make 2 changes:
# 1. Set `USE_GLES2` to 1 in gles_system.h
# 2. Define `__ANDROID__` in gles_system.cpp so that gzdoom loads the gles2 `.so`.
#
# Then, at runtime, we set `gl_es = 1` and `vid_preferbackend = 3`.
#
# See https://github.com/ZDoom/gzdoom/issues/1485
define GZDOOM_PATCH_USE_GLES2
	$(SED) 's%#define USE_GLES2 0%#define USE_GLES2 1%' \
        $(@D)/src/common/rendering/gles/gles_system.h
	$(SED) '1i #define __ANDROID__' $(@D)/src/common/rendering/gles/gles_system.cpp
endef

ifneq ($(BR2_PACKAGE_BATOCERA_TARGET_X86_64_ANY),y)
    GZDOOM_CONF_OPTS += -DHAVE_GLES2=ON
    GZDOOM_DEPENDENCIES += libgles
    GZDOOM_POST_PATCH_HOOKS += GZDOOM_PATCH_USE_GLES2
else
    GZDOOM_CONF_OPTS += -DHAVE_GLES2=OFF
    GZDOOM_DEPENDENCIES += libgl
endif

define GZDOOM_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/usr/share/gzdoom
	$(INSTALL) -m 0755 $(@D)/buildroot-build/gzdoom	$(TARGET_DIR)/usr/bin
	$(INSTALL) -m 0755 $(@D)/buildroot-build/*.pk3 $(TARGET_DIR)/usr/share/gzdoom
	cp -pr $(@D)/buildroot-build/fm_banks $(TARGET_DIR)/usr/share/gzdoom
	cp -pr $(@D)/buildroot-build/soundfonts $(TARGET_DIR)/usr/share/gzdoom
endef

define GZDOOM_PREPARE_VERSION_INFO
	export FALLBACK_GIT_TAG=$(GZDOOM_VERSION); \
	export FALLBACK_GIT_HASH=$(GZDOOM_HASH); \
	export FALLBACK_GIT_TIMESTAMP="$(shell date -u -Iseconds)"; \
	$(BR2_CMAKE) -P $(@D)/tools/updaterevision/UpdateRevision.cmake \
        $(@D)/src/gitinfo.h
	$(BR2_CMAKE) -P $(@D)/tools/updaterevision/UpdateRevision.cmake \
        $(GZDOOM_BUILDDIR)/src/gitinfo.h
endef

GZDOOM_POST_CONFIGURE_HOOKS += GZDOOM_PREPARE_VERSION_INFO

$(eval $(cmake-package))
$(eval $(host-cmake-package))
$(eval $(emulator-info-package))