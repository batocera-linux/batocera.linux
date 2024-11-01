################################################################################
#
# ecwolf
#
################################################################################
# Version: 2024-05-20
ECWOLF_VERSION = d1de69a576d4bb39e89124185a6dfd6991202cb9
ECWOLF_SITE = https://bitbucket.org/ecwolf/ecwolf.git
ECWOLF_SITE_METHOD=git
ECWOLF_GIT_SUBMODULES=YES
ECWOLF_LICENSE = Non-commercial
ECWOLF_DEPENDENCIES = host-ecwolf sdl2 sdl2_mixer sdl2_net zlib bzip2 jpeg
ECWOLF_SUPPORTS_IN_SOURCE_BUILD = NO

# We need the tools from the host package to build the target package
HOST_ECWOLF_DEPENDENCIES = zlib bzip2
HOST_ECWOLF_CONF_OPTS += -DTOOLS_ONLY=ON
HOST_ECWOLF_SUPPORTS_IN_SOURCE_BUILD = NO

define HOST_ECWOLF_INSTALL_CMDS
	# Skipping install, the tools are used directly via 
	# `ImportExecutables.cmake` from the build directory.
endef

ECWOLF_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release \
                    -DBUILD_SHARED_LIBS=OFF \
                    -DGPL=ON \
					-DIMPORT_EXECUTABLES="$(HOST_ECWOLF_BUILDDIR)/ImportExecutables.cmake" \
					-DFORCE_CROSSCOMPILE=ON \
					-DINTERNAL_JPEG=ON \
					-DINTERNAL_SDL_NET=ON \
					-DINTERNAL_SDL_MIXER=ON

# Copy the headers that are usually generated on the target machine
# but must be provided when cross-compiling.
ifeq ($(BR2_ARCH_IS_64),y)
ECWOLF_GENERATED_HEADER_SUFFIX = 64
else
ECWOLF_GENERATED_HEADER_SUFFIX = 32
endif

ECWOLF_CONF_INIT = $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/ports/ecwolf

define ECWOLF_COPY_GENERATED_HEADERS
	cp $(ECWOLF_CONF_INIT)/arith_$(ECWOLF_GENERATED_HEADER_SUFFIX).h \
	    $(ECWOLF_BUILDDIR)/deps/gdtoa/arith.h
	cp $(ECWOLF_CONF_INIT)/gd_qnan_$(ECWOLF_GENERATED_HEADER_SUFFIX).h \
	    $(ECWOLF_BUILDDIR)/deps/gdtoa/gd_qnan.h
endef

ECWOLF_POST_CONFIGURE_HOOKS += ECWOLF_COPY_GENERATED_HEADERS

define ECWOLF_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/usr/bin
	mkdir -p $(TARGET_DIR)/usr/share/ecwolf
	$(INSTALL) -D -m 0755 $(@D)/buildroot-build/ecwolf $(TARGET_DIR)/usr/share/ecwolf/ecwolf
	cp -a $(@D)/buildroot-build/ecwolf.pk3 $(TARGET_DIR)/usr/share/ecwolf/
	ln -sf /usr/share/ecwolf/ecwolf $(TARGET_DIR)/usr/bin/ecwolf

	# evmap config
	mkdir -p $(TARGET_DIR)/usr/share/evmapy
	cp $(ECWOLF_CONF_INIT)/ecwolf.keys $(TARGET_DIR)/usr/share/evmapy
endef

$(eval $(cmake-package))
$(eval $(host-cmake-package))
