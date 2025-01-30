################################################################################
#
# vkquake3
#
################################################################################
# Version: Commits on Jan 26, 2025
VKQUAKE3_VERSION = 5300b32803c1c61bc3b6bdf86a084c1db1a217ad
VKQUAKE3_SITE = $(call github,suijingfeng,vkQuake3,$(VKQUAKE3_VERSION))
VKQUAKE3_LICENSE = GPL-2.0
VKQUAKE3_LICENSE_FILE = COPYING.txt

VKQUAKE3_DEPENDENCIES = glslang opus opusfile sdl2 vulkan-headers vulkan-loader

VKQUAKE3_BUILD_ARGS += BUILD_SERVER=0
VKQUAKE3_BUILD_ARGS += BUILD_CLIENT=1
VKQUAKE3_BUILD_ARGS += BUILD_BASEGAME=1
VKQUAKE3_BUILD_ARGS += BUILD_MISSIONPACK=1
VKQUAKE3_BUILD_ARGS += BUILD_GAME_SO=0
VKQUAKE3_BUILD_ARGS += BUILD_GAME_QVM=0
VKQUAKE3_BUILD_ARGS += CROSS_COMPILING=1
VKQUAKE3_BUILD_ARGS += USE_RENDERER_DLOPEN=1

ifeq ($(BR2_aarch64),y)
    VKQUAKE3_BUILD_ARGS += COMPILE_ARCH=arm64
    VKQUAKE3_ARCH = arm64
else ifeq ($(BR2_arm),y)
    VKQUAKE3_BUILD_ARGS += COMPILE_ARCH=armv7l
    VKQUAKE3_ARCH = armv7l
else ifeq ($(BR2_x86_64),y)
    VKQUAKE3_BUILD_ARGS += COMPILE_ARCH=x86_64
    VKQUAKE3_ARCH = x86_64
endif

define VKQUAKE3_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" \
	    $(VKQUAKE3_BUILD_ARGS) SYSROOT=$(STAGING_DIR) -C $(@D) -f Makefile
endef

define VKQUAKE3_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/usr/bin/ioquake3
	$(INSTALL) -D $(@D)/build/release-linux-$(VKQUAKE3_ARCH)/ioquake3.$(VKQUAKE3_ARCH) \
		$(TARGET_DIR)/usr/bin/ioquake3/ioquake3
	$(INSTALL) -D $(@D)/build/release-linux-$(VKQUAKE3_ARCH)/renderer_opengl1_$(VKQUAKE3_ARCH).so \
		$(TARGET_DIR)/usr/bin/ioquake3/
	$(INSTALL) -D $(@D)/build/release-linux-$(VKQUAKE3_ARCH)/renderer_opengl2_$(VKQUAKE3_ARCH).so \
		$(TARGET_DIR)/usr/bin/ioquake3/
	$(INSTALL) -D $(@D)/build/release-linux-$(VKQUAKE3_ARCH)/renderer_vulkan_$(VKQUAKE3_ARCH).so \
	    $(TARGET_DIR)/usr/bin/ioquake3/
endef

define VKQUAKE3_EVMAPY
	mkdir -p $(TARGET_DIR)/usr/share/evmapy
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/ports/vkquake3/quake3.keys \
	    $(TARGET_DIR)/usr/share/evmapy
endef

VKQUAKE3_POST_INSTALL_TARGET_HOOKS += VKQUAKE3_EVMAPY

$(eval $(generic-package))
