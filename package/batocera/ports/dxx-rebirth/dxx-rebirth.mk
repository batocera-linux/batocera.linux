################################################################################
#
# dxx-rebirth (Descent 1 & 2) engine
#
################################################################################
# Version: Commits on Aug 12, 2024
DXX_REBIRTH_VERSION = bd3c033bdf1faa4606086dcae0436531fb2e7e5c
DXX_REBIRTH_SITE = https://github.com/dxx-rebirth/dxx-rebirth
DXX_REBIRTH_SITE_METHOD=git
DXX_REBIRTH_LICENSE = GPLv3
DXX_REBIRTH_LICENSE_FILE = COPYING.txt
DXX_REBIRTH_DEPENDENCIES = host-scons sdl2 sdl2_image sdl2_mixer libpng physfs

DXX_REBIRTH_LDFLAGS   = $(TARGET_LDFLAGS)
DXX_REBIRTH_CFLAGS    = $(TARGET_CFLAGS)
DXX_REBIRTH_CXXFLAGS  = $(TARGET_CXXFLAGS)
DXX_REBIRTH_SCONS_ENV = $(TARGET_CONFIGURE_OPTS)

DXX_REBIRTH_SCONS_OPTS = -j$(PARALLEL_JOBS)

DXX_REBIRTH_SCONS_OPTS += sdl2=yes

define DXX_REBIRTH_BUILD_CMDS
    (cd $(@D); \
        PKG_CONFIG_PATH="$(STAGING_DIR)/usr/lib/pkgconfig" \
        $(DXX_REBIRTH_SCONS_ENV) \
        $(SCONS) \
        $(DXX_REBIRTH_SCONS_OPTS))
endef

define DXX_REBIRTH_INSTALL_TARGET_CMDS
    cp $(@D)/build/d1x-rebirth/d1x-rebirth $(TARGET_DIR)/usr/bin/
    cp $(@D)/build/d2x-rebirth/d2x-rebirth $(TARGET_DIR)/usr/bin/
endef

define DXX_REBIRTH_EVMAPY
	mkdir -p $(TARGET_DIR)/usr/share/evmapy
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/ports/dxx-rebirth/dxx-rebirth.keys \
	    $(TARGET_DIR)/usr/share/evmapy
endef

DXX_REBIRTH_POST_INSTALL_TARGET_HOOKS += DXX_REBIRTH_EVMAPY

$(eval $(generic-package))
