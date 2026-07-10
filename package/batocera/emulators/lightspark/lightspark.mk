################################################################################
#
# lightspark
#
################################################################################

LIGHTSPARK_VERSION = 53eac9d5d4066568c97dac1a03be95c2e144478a
LIGHTSPARK_SITE = $(call github,lightspark,lightspark,$(LIGHTSPARK_VERSION))
LIGHTSPARK_LICENSE = LGPLv3
LIGHTSPARK_DEPENDENCIES = sdl2 freetype pcre2 jpeg libpng cairo pango
LIGHTSPARK_DEPENDENCIES +=  ffmpeg libcurl rtmpdump
LIGHTSPARK_EMULATOR_INFO = lightspark.emulator.yml

LIGHTSPARK_CONF_OPTS = -DCOMPILE_NPAPI_PLUGIN=FALSE
LIGHTSPARK_CONF_OPTS += -DCOMPILE_PPAPI_PLUGIN=FALSE

LIGHTSPARK_ARCH = $(BR2_ARCH)

ifneq ($(BR2_x86_64),y)
LIGHTSPARK_CONF_OPTS += -DCMAKE_C_FLAGS=-DEGL_NO_X11
LIGHTSPARK_CONF_OPTS += -DCMAKE_CXX_FLAGS=-DEGL_NO_X11
LIGHTSPARK_CONF_OPTS += -DENABLE_SSE2=OFF
endif

ifeq ($(LIGHTSPARK_ARCH), "arm")
LIGHTSPARK_ARCH = armv7l
endif

ifeq ($(BR2_PACKAGE_BATOCERA_GLES3),y)
LIGHTSPARK_CONF_OPTS += -DENABLE_GLES3=ON
LIGHTSPARK_DEPENDENCIES += libgles
else ifeq ($(BR2_PACKAGE_BATOCERA_GLES2),y)
LIGHTSPARK_CONF_OPTS += -DENABLE_GLES2=ON
LIGHTSPARK_DEPENDENCIES += libgles
endif

define LIGHTSPARK_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/usr/bin
	mkdir -p $(TARGET_DIR)/usr/lib
	cp -pr $(@D)/$(LIGHTSPARK_ARCH)/Release/bin/lightspark \
	    $(TARGET_DIR)/usr/bin/lightspark
	cp -pr $(@D)/$(LIGHTSPARK_ARCH)/Release/lib/* \
	    $(TARGET_DIR)/usr/lib/
endef

$(eval $(cmake-package))
$(eval $(emulator-info-package))
