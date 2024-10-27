################################################################################
#
# iortcw
#
################################################################################
# Version: Commits on May 27, 2024
IORTCW_VERSION = 438e7d413b5f7277187c35b032eb0ef9093ae778
IORTCW_SITE = https://github.com/iortcw/iortcw.git
IORTCW_SITE_METHOD = git
IORTCW_GIT_SUBMODULES=YES
IORTCW_LICENSE = GPL-3.0
IORTCW_LICENSE_FILE = COPYING

IORTCW_DEPENDENCIES = sdl2 openal

# Common args
IORTCW_BUILD_ARGS += BUILD_SERVER=0
IORTCW_BUILD_ARGS += BUILD_CLIENT=1
IORTCW_BUILD_ARGS += BUILD_BASEGAME=1
IORTCW_BUILD_ARGS += BUILD_GAME_SO=1
IORTCW_BUILD_ARGS += BUILD_GAME_QVM=0
IORTCW_BUILD_ARGS += CROSS_COMPILING=1
IORTCW_BUILD_ARGS += USE_RENDERER_DLOPEN=1
IORTCW_BUILD_ARGS += USE_LOCAL_HEADERS=1
IORTCW_BUILD_ARGS += USE_INTERNAL_JPEG=1
IORTCW_BUILD_ARGS += USE_INTERNAL_OPUS=1
IORTCW_BUILD_ARGS += USE_INTERNAL_ZLIB=1
IORTCW_BUILD_ARGS += USE_OPENAL=1
IORTCW_BUILD_ARGS += USE_OPENAL_DLOPEN=1
IORTCW_BUILD_ARGS += USE_XDG=1

ifeq ($(BR2_x86_64),y)
    IORTCW_BUILD_ARGS += COMPILE_ARCH=x86_64
    IORTCW_ARCH = x86_64
    IORTCW_BUILD_ARGS += USE_VOIP=1
    IORTCW_BUILD_ARGS += USE_CODEC_VORBIS=1
    IORTCW_BUILD_ARGS += USE_CODEC_OPUS=1
    IORTCW_BUILD_ARGS += USE_BLOOM=1
    IORTCW_BUILD_ARGS += USE_MUMBLE=1
    IORTCW_BUILD_ARGS += BUILD_RENDERER_REND2=1
else ifeq ($(BR2_aarch64),y)
    IORTCW_BUILD_ARGS += COMPILE_ARCH=arm64
    IORTCW_ARCH = arm64
    IORTCW_BUILD_ARGS += USE_VOIP=0
    IORTCW_BUILD_ARGS += USE_CODEC_VORBIS=0
    IORTCW_BUILD_ARGS += USE_CODEC_OPUS=0
    IORTCW_BUILD_ARGS += USE_CURL=0
    IORTCW_BUILD_ARGS += USE_CURL_DLOPEN=0
    IORTCW_BUILD_ARGS += USE_RENDERER_DLOPEN=0
    IORTCW_BUILD_ARGS += USE_OPENGLES=1
    IORTCW_BUILD_ARGS += USE_BLOOM=0
    IORTCW_BUILD_ARGS += USE_MUMBLE=0
    IORTCW_BUILD_ARGS += BUILD_RENDERER_REND2=0
endif

define IORTCW_BUILD_CMDS
    # Single player
    $(MAKE) $(TARGET_CONFIGURE_OPTS) $(IORTCW_BUILD_ARGS) -C $(@D)/SP
    # Multi player
    $(MAKE) $(TARGET_CONFIGURE_OPTS) $(IORTCW_BUILD_ARGS) -C $(@D)/MP
endef

IORTCW_CONF_INIT = $(TARGET_DIR)/usr/share/batocera/datainit/roms/iortcw/main

define IORTCW_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/usr/bin/iortcw/main
    mkdir -p $(TARGET_DIR)/usr/bin/iortcw
	
	# Single player
	$(INSTALL) -D $(@D)/SP/build/release-linux-$(IORTCW_ARCH)/iowolfsp.$(IORTCW_ARCH) $(TARGET_DIR)/usr/bin/iortcw/iowolfsp
	$(INSTALL) -D $(@D)/SP/build/release-linux-$(IORTCW_ARCH)/main/*.so $(TARGET_DIR)/usr/bin/iortcw/main/
	
    # Multi player
	$(INSTALL) -D $(@D)/MP/build/release-linux-$(IORTCW_ARCH)/iowolfmp.$(IORTCW_ARCH) $(TARGET_DIR)/usr/bin/iortcw/iowolfmp
	$(INSTALL) -D $(@D)/MP/build/release-linux-$(IORTCW_ARCH)/main/*.so $(TARGET_DIR)/usr/bin/iortcw/main/

    # Additions if x86_64
    $(if $(BR2_x86_64),\
		$(INSTALL) -D $(@D)/SP/build/release-linux-$(IORTCW_ARCH)/renderer_sp*.so $(TARGET_DIR)/usr/bin/iortcw/; \
		$(INSTALL) -D $(@D)/MP/build/release-linux-$(IORTCW_ARCH)/renderer_mp*.so $(TARGET_DIR)/usr/bin/iortcw/;)
endef

# required to have fullscreen at 1st start
define IORTCW_CONFIG_FILE
    mkdir -p $(IORTCW_CONF_INIT)
    cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/ports/iortcw/wolfconfig.cfg \
        $(IORTCW_CONF_INIT)
endef

define IORTCW_EVMAPY
	mkdir -p $(TARGET_DIR)/usr/share/evmapy
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/ports/iortcw/iortcw.keys \
	    $(TARGET_DIR)/usr/share/evmapy
endef

IORTCW_POST_INSTALL_TARGET_HOOKS += IORTCW_CONFIG_FILE
IORTCW_POST_INSTALL_TARGET_HOOKS += IORTCW_EVMAPY

$(eval $(generic-package))
