################################################################################
#
# ioquake3
#
################################################################################
# Version: Commits on Dec 25, 2024
IOQUAKE3_VERSION = 3fb9006e6461b877b67781cd0f0d94032804a475
IOQUAKE3_SITE = $(call github,ioquake,ioq3,$(IOQUAKE3_VERSION))
IOQUAKE3_LICENSE = GPL-2.0
IOQUAKE3_LICENSE_FILE = COPYING.txt

IOQUAKE3_DEPENDENCIES = libcurl libogg libvorbis libzlib openal opus sdl2 

IOQUAKE3_BUILD_ARGS += BUILD_SERVER=0
IOQUAKE3_BUILD_ARGS += BUILD_CLIENT=1
IOQUAKE3_BUILD_ARGS += BUILD_BASEGAME=1
IOQUAKE3_BUILD_ARGS += BUILD_MISSIONPACK=1
IOQUAKE3_BUILD_ARGS += BUILD_GAME_SO=0
IOQUAKE3_BUILD_ARGS += BUILD_GAME_QVM=0
IOQUAKE3_BUILD_ARGS += CROSS_COMPILING=1
IOQUAKE3_BUILD_ARGS += USE_RENDERER_DLOPEN=1

ifeq ($(BR2_PACKAGE_HAS_LIBGL),y)
    IOQUAKE3_DEPENDENCIES += libgl
endif

ifeq ($(BR2_PACKAGE_HAS_LIBGLES),y)
    IOQUAKE3_DEPENDENCIES += libgles
endif

ifeq ($(BR2_aarch64),y)
    IOQUAKE3_BUILD_ARGS += COMPILE_ARCH=arm64
    IOQUAKE3_ARCH = arm64
else ifeq ($(BR2_arm),y)
    IOQUAKE3_BUILD_ARGS += COMPILE_ARCH=armv7l
    IOQUAKE3_ARCH = armv7l
else ifeq ($(BR2_x86_64),y)
    IOQUAKE3_BUILD_ARGS += COMPILE_ARCH=x86_64
    IOQUAKE3_ARCH = x86_64
endif

define IOQUAKE3_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" \
	    $(IOQUAKE3_BUILD_ARGS) SYSROOT=$(STAGING_DIR) -C $(@D) -f Makefile
endef

define IOQUAKE3_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/usr/bin/ioquake3
	$(INSTALL) -D $(@D)/build/release-linux-$(IOQUAKE3_ARCH)/ioquake3.$(IOQUAKE3_ARCH) \
		$(TARGET_DIR)/usr/bin/ioquake3/ioquake3
	$(INSTALL) -D $(@D)/build/release-linux-$(IOQUAKE3_ARCH)/renderer_opengl1_$(IOQUAKE3_ARCH).so \
		$(TARGET_DIR)/usr/bin/ioquake3/
	$(INSTALL) -D $(@D)/build/release-linux-$(IOQUAKE3_ARCH)/renderer_opengl2_$(IOQUAKE3_ARCH).so \
		$(TARGET_DIR)/usr/bin/ioquake3/
endef

define IOQUAKE3_EVMAPY
	mkdir -p $(TARGET_DIR)/usr/share/evmapy
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/ports/ioquake3/quake3.keys \
	    $(TARGET_DIR)/usr/share/evmapy
endef

IOQUAKE3_POST_INSTALL_TARGET_HOOKS += IOQUAKE3_EVMAPY

$(eval $(generic-package))
