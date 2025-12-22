################################################################################
#
# yquake2
#
################################################################################

YQUAKE2_VERSION = QUAKE2_8_60
YQUAKE2_SITE = $(call github,yquake2,yquake2,$(YQUAKE2_VERSION))
YQUAKE2_LICENSE = GPLv2
YQUAKE2_LICENSE_FILES = LICENSE

YQUAKE2_BUILD_ARGS = WITH_SYSTEMWIDE=yes \
	WITH_SYSTEMDIR=/userdata/roms/quake2 \
	INCLUDE= LDFLAGS= \
	YQ2_OSTYPE=Linux

ifeq ($(BR2_PACKAGE_SDL3),y)
    YQUAKE2_DEPENDENCIES += sdl3
    YQUAKE2_BUILD_ARGS += WITH_SDL3=yes
else
    YQUAKE2_DEPENDENCIES += sdl2
    YQUAKE2_BUILD_ARGS += WITH_SDL3=no
endif

ifeq ($(BR2_PACKAGE_OPENAL),y)
    YQUAKE2_DEPENDENCIES += openal
else
    YQUAKE2_BUILD_ARGS += WITH_OPENAL=no
endif

ifeq ($(BR2_PACKAGE_LIBCURL),y)
    YQUAKE2_DEPENDENCIES += libcurl
else
    YQUAKE2_BUILD_ARGS += WITH_CURL=no
endif

ifeq ($(BR2_aarch64),y)
    YQUAKE2_BUILD_ARGS += YQ2_ARCH=aarch64
else ifeq ($(BR2_arm),y)
    YQUAKE2_BUILD_ARGS += YQ2_ARCH=arm
else ifeq ($(BR2_x86_64),y)
    YQUAKE2_BUILD_ARGS += YQ2_ARCH=x86_64
else ifeq ($(BR2_i386),y)
    YQUAKE2_BUILD_ARGS += YQ2_ARCH=i386
endif

# Delete the following line once the hidraw/hidapi conflict gets solved
YQUAKE2_BUILD_ARGS += NO_SDL_GYRO=On

# Available renderers in the current target

YQUAKE2_BUILD_ARGS += config client game ref_soft

ifeq ($(BR2_PACKAGE_HAS_LIBGLES),y)
    YQUAKE2_BUILD_ARGS += ref_gles1
endif
ifeq ($(BR2_PACKAGE_HAS_LIBGL),y)
    YQUAKE2_BUILD_ARGS += ref_gl1 ref_gl3
endif
ifeq ($(BR2_PACKAGE_BATOCERA_GLES3),y)
    YQUAKE2_BUILD_ARGS += ref_gles3
endif

# Build & install

define YQUAKE2_BUILD_CMDS
    $(MAKE) $(TARGET_CONFIGURE_OPTS) $(YQUAKE2_BUILD_ARGS) -C $(@D)
endef

define YQUAKE2_INSTALL_TARGET_CMDS
    mkdir -p $(TARGET_DIR)/usr/bin/yquake2
    $(INSTALL) -D $(@D)/release/quake2 \
        $(TARGET_DIR)/usr/bin/yquake2/
    $(INSTALL) -D -m 0644 $(@D)/release/ref_*.so \
        $(TARGET_DIR)/usr/bin/yquake2/
    mkdir -p $(TARGET_DIR)/usr/bin/yquake2/baseq2
    $(INSTALL) -D -m 0644 $(@D)/release/baseq2/game.so \
        $(TARGET_DIR)/usr/bin/yquake2/baseq2/
endef

$(eval $(generic-package))
