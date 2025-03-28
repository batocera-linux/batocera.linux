################################################################################
#
# lightspark
#
################################################################################
# Version.: Commits on May 28, 2023
LIGHTSPARK_VERSION = 0.8.7
LIGHTSPARK_SITE = $(call github,lightspark,lightspark,$(LIGHTSPARK_VERSION))
LIGHTSPARK_LICENSE = LGPLv3
LIGHTSPARK_DEPENDENCIES = sdl2 freetype pcre jpeg libpng cairo pango ffmpeg libcurl rtmpdump

LIGHTSPARK_CONF_OPTS += -DCOMPILE_NPAPI_PLUGIN=FALSE -DCOMPILE_PPAPI_PLUGIN=FALSE

LIGHTSPARK_ARCH = $(BR2_ARCH)

ifeq ($(BR2_PACKAGE_XORG7)$(BR2_PACKAGE_HAS_LIBGL),yy)
LIGHTSPARK_DEPENDENCIES += libglew
endif

ifneq ($(BR2_x86_64),y)
LIGHTSPARK_CONF_OPTS += -DENABLE_GLES2=TRUE
LIGHTSPARK_CONF_OPTS += -DCMAKE_C_FLAGS=-DEGL_NO_X11
LIGHTSPARK_CONF_OPTS += -DCMAKE_CXX_FLAGS=-DEGL_NO_X11
endif

ifeq ($(LIGHTSPARK_ARCH), "arm")
LIGHTSPARK_ARCH = armv7l
endif

define LIGHTSPARK_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/usr/bin
	mkdir -p $(TARGET_DIR)/usr/lib
	mkdir -p $(TARGET_DIR)/usr/share/evmapy

	cp -pr $(@D)/$(LIGHTSPARK_ARCH)/Release/bin/lightspark $(TARGET_DIR)/usr/bin/lightspark
	cp -pr $(@D)/$(LIGHTSPARK_ARCH)/Release/lib/*          $(TARGET_DIR)/usr/lib/
endef

$(eval $(cmake-package))
