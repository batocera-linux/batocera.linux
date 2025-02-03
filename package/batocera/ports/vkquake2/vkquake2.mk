################################################################################
#
# vkquake2
#
################################################################################
# Version: Commits on Jan 5, 2025
VKQUAKE2_VERSION = 5bf9c012024884234df0f63c615daec0c740def7
VKQUAKE2_SITE = $(call github,kondrak,vkQuake2,$(VKQUAKE2_VERSION))
VKQUAKE2_LICENSE = GPL-2.0
VKQUAKE2_LICENSE_FILE = LICENSE

VKQUAKE2_DEPENDENCIES = alsa-lib glslang libglu vulkan-headers vulkan-loader
VKQUAKE2_DEPENDENCIES += xlib_libXxf86dga xlib_libXxf86vm

ifeq ($(BR2_aarch64),y)
    VKQUAKE2_ARCH = aarch64
else ifeq ($(BR2_arm),y)
    VKQUAKE2_ARCH = armv7l
else ifeq ($(BR2_x86_64),y)
    VKQUAKE2_ARCH = x64
endif

VKQUAKE2_BASE_CFLAGS = -I$(STAGING_DIR)/usr/include -Dstricmp=strcasecmp -D_GNU_SOURCE
VKQUAKE2_BASE_CFLAGS += -Wno-format-truncation -Wno-unused-result -Wno-format-overflow

VKQUAKE2_MAKE_OPTS = $(TARGET_CONFIGURE_OPTS) \
	KERNEL_ARCH="$(VKQUAKE2_ARCH)" \
	BASE_CFLAGS="$(VKQUAKE2_BASE_CFLAGS)" \
	GLCFLAGS="-I$(STAGING_DIR)/usr/include" \
	VKCFLAGS="-I$(STAGING_DIR)/usr/include" \
	LDFLAGS="-L$(STAGING_DIR)/usr/lib -ldl -lm -lasound -lpthread" \
	GLLDFLAGS="-L$(STAGING_DIR)/usr/lib -lX11 -lXext -lvga -lm" \
	GLXLDFLAGS="-L$(STAGING_DIR)/usr/lib -lX11 -lXext -lXxf86dga -lXxf86vm -lm" \
	VKLDFLAGS="-L$(STAGING_DIR)/usr/lib -lX11 -lXext -lXxf86dga -lXxf86vm -lm -lvulkan -lstdc++" \
	XLDFLAGS="-L$(STAGING_DIR)/usr/lib -lX11 -lXext -lXxf86dga"

define VKQUAKE2_BUILD_CMDS
	$(MAKE) -C $(@D)/linux release \
	    $(VKQUAKE2_MAKE_OPTS)
endef

define VKQUAKE2_INSTALL_TARGET_CMDS
    mkdir -p $(TARGET_DIR)/usr/bin/vkquake2
	cp -f $(@D)/linux/release$(VKQUAKE2_ARCH)/quake2 \
	    $(TARGET_DIR)/usr/bin/vkquake2/
	cp -f $(@D)/linux/release$(VKQUAKE2_ARCH)/ref*.so \
	    $(TARGET_DIR)/usr/bin/vkquake2/
	mkdir -p $(TARGET_DIR)/usr/bin/vkquake2/baseq2
	cp -f $(@D)/linux/release$(VKQUAKE2_ARCH)/baseq2/*.so \
	    $(TARGET_DIR)/usr/bin/vkquake2/baseq2/
	mkdir -p $(TARGET_DIR)/usr/bin/vkquake2/ctf
	cp -f $(@D)/linux/release$(VKQUAKE2_ARCH)/ctf/*.so \
	    $(TARGET_DIR)/usr/bin/vkquake2/ctf/
	mkdir -p $(TARGET_DIR)/usr/bin/vkquake2/rogue
	cp -f $(@D)/linux/release$(VKQUAKE2_ARCH)/rogue/*.so \
	    $(TARGET_DIR)/usr/bin/vkquake2/rogue/
	mkdir -p $(TARGET_DIR)/usr/bin/vkquake2/smd
	cp -f $(@D)/linux/release$(VKQUAKE2_ARCH)/smd/*.so \
	    $(TARGET_DIR)/usr/bin/vkquake2/smd/
	mkdir -p $(TARGET_DIR)/usr/bin/vkquake2/xatrix
	cp -f $(@D)/linux/release$(VKQUAKE2_ARCH)/xatrix/*.so \
	    $(TARGET_DIR)/usr/bin/vkquake2/xatrix/
	mkdir -p $(TARGET_DIR)/usr/bin/vkquake2/zaero
	cp -f $(@D)/linux/release$(VKQUAKE2_ARCH)/zaero/*.so \
	    $(TARGET_DIR)/usr/bin/vkquake2/zaero/
endef

define VKQUAKE2_EVMAPY
	mkdir -p $(TARGET_DIR)/usr/share/evmapy
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/ports/vkquake2/quake2.keys \
	    $(TARGET_DIR)/usr/share/evmapy
endef

VKQUAKE2_POST_INSTALL_TARGET_HOOKS += VKQUAKE2_EVMAPY

$(eval $(generic-package))
