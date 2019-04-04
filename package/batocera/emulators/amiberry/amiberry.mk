################################################################################
#
# AMIBERRY
#
################################################################################

AMIBERRY_VERSION = aafa0a03c661cea12cf3c20d8cecb09d89247ba1
AMIBERRY_SITE = $(call github,midwan,amiberry,$(AMIBERRY_VERSION))
AMIBERRY_DEPENDENCIES = sdl2 sdl2_image sdl_gfx sdl2_ttf mpg123 libxml2 libmpeg2 guichan flac rpi-userland

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI3),y)
	AMIBERRY_BATOCERA_SYSTEM=rpi3-sdl2
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI2),y)
	AMIBERRY_BATOCERA_SYSTEM=rpi2-sdl2
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI1),y)
	AMIBERRY_BATOCERA_SYSTEM=rpi1-sdl2
endif

define AMIBERRY_CONFIGURE_PI
	sed -i "s+/opt/vc+$(STAGING_DIR)/usr+g" $(@D)/Makefile
endef

AMIBERRY_PRE_CONFIGURE_HOOKS += AMIBERRY_CONFIGURE_PI

define AMIBERRY_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) \
		CPP="$(TARGET_CPP)" \
		CXX="$(TARGET_CXX)" \
		CC="$(TARGET_CC)" \
		AS="$(TARGET_CC)" \
		STRIP="$(TARGET_STRIP)" \
                SDL_CONFIG=$(STAGING_DIR)/usr/bin/sdl2-config \
		-C $(@D) PLATFORM=$(AMIBERRY_BATOCERA_SYSTEM)
endef

define AMIBERRY_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/amiberry-$(AMIBERRY_BATOCERA_SYSTEM) $(TARGET_DIR)/usr/bin/amiberry
        mkdir -p $(TARGET_DIR)/usr/share/amiberry
	ln -sf /userdata/system/configs/amiberry/whdboot $(TARGET_DIR)/usr/share/amiberry/whdboot
        mkdir -p $(TARGET_DIR)/usr/share/batocera/datainit/system/configs/amiberry
	cp -pr $(@D)/whdboot $(TARGET_DIR)/usr/share/batocera/datainit/system/configs/amiberry/
	cp -rf $(@D)/data $(TARGET_DIR)/usr/share/amiberry
endef

$(eval $(generic-package))
