################################################################################
#
# AMIBERRY
#
################################################################################
# Version.: Commits on Feb 18, 2020
AMIBERRY_VERSION = v3.1.3
AMIBERRY_SITE = $(call github,midwan,amiberry,$(AMIBERRY_VERSION))
AMIBERRY_LICENSE = GPLv3
AMIBERRY_DEPENDENCIES = sdl2 sdl2_image sdl2_ttf mpg123 libxml2 libmpeg2 flac

ifeq ($(BR2_PACKAGE_RPI_USERLAND),y)
	AMIBERRY_DEPENDENCIES += rpi-userland
endif

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI3),y)
	AMIBERRY_BATOCERA_SYSTEM=rpi3-sdl2
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI2),y)
	AMIBERRY_BATOCERA_SYSTEM=rpi2-sdl2
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI1),y)
	AMIBERRY_BATOCERA_SYSTEM=rpi1-sdl2
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_XU4),y)
	AMIBERRY_BATOCERA_SYSTEM=xu4
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_ODROIDN2),y)
	AMIBERRY_BATOCERA_SYSTEM=AMLG12B
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_ODROIDGOA),y)
	AMIBERRY_BATOCERA_SYSTEM=RK3326
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_ROCKPRO64),y)
	AMIBERRY_BATOCERA_SYSTEM=RK3399
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_ROCK960),y)
	AMIBERRY_BATOCERA_SYSTEM=RK3399
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_TINKERBOARD),y)
	AMIBERRY_BATOCERA_SYSTEM=RK3288
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_MIQI),y)
	AMIBERRY_BATOCERA_SYSTEM=RK3288
endif

define AMIBERRY_CONFIGURE_PI
	sed -i "s+/opt/vc+$(STAGING_DIR)/usr+g" $(@D)/Makefile
	sed -i "s+xml2-config+$(STAGING_DIR)/usr/bin/xml2-config+g" $(@D)/Makefile
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
		-C $(@D) \
		-f Makefile \
		PLATFORM=$(AMIBERRY_BATOCERA_SYSTEM)
endef

define AMIBERRY_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/amiberry $(TARGET_DIR)/usr/bin/amiberry
        mkdir -p $(TARGET_DIR)/usr/share/amiberry

	ln -sf /userdata/system/configs/amiberry/whdboot $(TARGET_DIR)/usr/share/amiberry/whdboot
        mkdir -p $(TARGET_DIR)/usr/share/batocera/datainit/system/configs/amiberry
		
	cp -pr $(@D)/whdboot $(TARGET_DIR)/usr/share/batocera/datainit/system/configs/amiberry/
	cp -rf $(@D)/data $(TARGET_DIR)/usr/share/amiberry
endef

$(eval $(generic-package))
