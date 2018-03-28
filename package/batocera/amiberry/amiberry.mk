################################################################################
#
# AMIBERRY
#
################################################################################

AMIBERRY_VERSION = 1f27fdf4f55302068e0419783ff0d6972dff5e1c
AMIBERRY_SITE = $(call github,midwan,amiberry,$(AMIBERRY_VERSION))
AMIBERRY_DEPENDENCIES = sdl sdl_image sdl_gfx sdl_ttf mpg123 libxml2 libmpeg2 guichan flac rpi-userland

ifeq ($(BR2_PACKAGE_RECALBOX_TARGET_RPI3),y)
	RECALBOX_SYSTEM=rpi3
else ifeq ($(BR2_PACKAGE_RECALBOX_TARGET_RPI2),y)
	RECALBOX_SYSTEM=rpi2
else ifeq ($(BR2_PACKAGE_RECALBOX_TARGET_RPI1),y)
	RECALBOX_SYSTEM=rpi1
else ifeq ($(BR2_PACKAGE_RECALBOX_TARGET_XU4)$(BR2_PACKAGE_RECALBOX_TARGET_LEGACYXU4),y)
	RECALBOX_SYSTEM=odroidxu4
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
                SDL_CONFIG=$(STAGING_DIR)/usr/bin/sdl-config \
		-C $(@D) PLATFORM=$(RECALBOX_SYSTEM)
endef

define AMIBERRY_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/amiberry $(TARGET_DIR)/usr/bin/amiberry
	rm -rf $(TARGET_DIR)/usr/share/amiberry/data
	mkdir -p $(TARGET_DIR)/usr/share/amiberry
	cp -r $(@D)/data $(TARGET_DIR)/usr/share/amiberry
endef

$(eval $(generic-package))
