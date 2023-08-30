################################################################################
#
# dxx-rebirth (Descent 1 & 2) engine
#
################################################################################

DXX_REBIRTH_VERSION = 5c900ca7a72398a9d9e46428cb1d684eba0a5cc5
DXX_REBIRTH_SITE = https://github.com/dxx-rebirth/dxx-rebirth
DXX_REBIRTH_SITE_METHOD=git
DXX_REBIRTH_DEPENDENCIES = host-scons sdl2 sdl2_image sdl2_mixer libpng physfs

DXX_REBIRTH_LDFLAGS = $(TARGET_LDFLAGS)
DXX_REBIRTH_CFLAGS = $(TARGET_CFLAGS)
DXX_REBIRTH_CXXFLAGS = $(TARGET_CXXFLAGS)
DXX_REBIRTH_SCONS_ENV = $(TARGET_CONFIGURE_OPTS)

DXX_REBIRTH_SCONS_OPTS = -j$(PARALLEL_JOBS) sdl2=yes

# dxx-rebirth currently does not support sdl2 + opengles combo
ifneq ($(BR2_PACKAGE_HAS_LIBGL),y)
DXX_REBIRTH_SCONS_OPTS += opengles=yes
endif

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

$(eval $(generic-package))
