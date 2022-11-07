################################################################################
#
# gzdoom
#
################################################################################
GZDOOM_VERSION = g4.8.2
GZDOOM_SITE = https://github.com/coelckers/gzdoom.git
GZDOOM_SITE_METHOD=git
GZDOOM_GIT_SUBMODULES=YES
GZDOOM_LICENSE = GPLv3
GZDOOM_DEPENDENCIES = host-gzdoom sdl2 bzip2 fluidsynth libgtk3 openal mesa3d libglu libglew zmusic
GZDOOM_SUPPORTS_IN_SOURCE_BUILD = NO

# We need the tools from the host package to build the target package
HOST_GZDOOM_DEPENDENCIES = zlib bzip2
HOST_GZDOOM_CONF_OPTS += -DTOOLS_ONLY=ON -DSKIP_INSTALL_ALL=ON -DCMAKE_BUILD_TYPE=Release
HOST_GZDOOM_SUPPORTS_IN_SOURCE_BUILD = NO

define HOST_GZDOOM_INSTALL_CMDS
	# Skipping install, the tools are used directly via `ImportExecutables.cmake` from the build directory.
endef

GZDOOM_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release
GZDOOM_CONF_OPTS += -DFORCE_CROSSCOMPILE=ON
GZDOOM_CONF_OPTS += -DBUILD_SHARED_LIBS=OFF
GZDOOM_CONF_OPTS += -DIMPORT_EXECUTABLES="$(HOST_GZDOOM_BUILDDIR)/ImportExecutables.cmake"

# Copy the headers that are usually generated on the target machine
# but must be provided when cross-compiling.
define GZDOOM_COPY_GENERATED_HEADERS
	mkdir -p $(GZDOOM_BUILDDIR)/libraries/gdtoa/
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/ports/gzdoom/*.h $(GZDOOM_BUILDDIR)/libraries/gdtoa/
endef

GZDOOM_PRE_CONFIGURE_HOOKS += GZDOOM_COPY_GENERATED_HEADERS

ifeq ($(BR2_PACKAGE_VULKAN_HEADERS)$(BR2_PACKAGE_VULKAN_LOADER),yy)
    GZDOOM_CONF_OPTS += -DHAVE_VULKAN=ON
else
    GZDOOM_CONF_OPTS += -DHAVE_VULKAN=OFF
endif

ifeq ($(BR2_PACKAGE_BATOCERA_GLES2),y)
    GZDOOM_CONF_OPTS += -DHAVE_GLES2=ON
else
    GZDOOM_CONF_OPTS += -DHAVE_GLES2=OFF
endif

define GZDOOM_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/usr/share/gzdoom
	$(INSTALL) -m 0755 $(@D)/buildroot-build/gzdoom	$(TARGET_DIR)/usr/bin
	$(INSTALL) -m 0755 $(@D)/buildroot-build/*.pk3 $(TARGET_DIR)/usr/share/gzdoom
	cp -pr $(@D)/buildroot-build/fm_banks $(TARGET_DIR)/usr/share/gzdoom
	cp -pr $(@D)/buildroot-build/soundfonts $(TARGET_DIR)/usr/share/gzdoom
	mkdir -p $(TARGET_DIR)/usr/share/evmapy
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/ports/gzdoom/gzdoom.keys $(TARGET_DIR)/usr/share/evmapy
endef

$(eval $(cmake-package))
$(eval $(host-cmake-package))
