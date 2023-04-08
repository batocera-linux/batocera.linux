################################################################################
#
# AMIBERRY
#
################################################################################

AMIBERRY_VERSION = v5.6.0
AMIBERRY_SITE = $(call github,BlitterStudio,amiberry,$(AMIBERRY_VERSION))
AMIBERRY_LICENSE = GPLv3
AMIBERRY_DEPENDENCIES = sdl2 sdl2_image sdl2_ttf mpg123 libxml2 libmpeg2 flac libpng libserialport

ifeq ($(BR2_PACKAGE_RPI_USERLAND),y)
	AMIBERRY_DEPENDENCIES += rpi-userland
endif

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2711),y)
	AMIBERRY_BATOCERA_SYSTEM=rpi4-64-sdl2
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2837),y)
    AMIBERRY_BATOCERA_SYSTEM=rpi3-64-sdl2
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2836),y)
	AMIBERRY_BATOCERA_SYSTEM=rpi2-sdl2
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2835),y)
	AMIBERRY_BATOCERA_SYSTEM=rpi1-sdl2
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_XU4),y)
	AMIBERRY_BATOCERA_SYSTEM=xu4
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_S922X),y)
	AMIBERRY_BATOCERA_SYSTEM=AMLG12B
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_TRITIUM_H5),y)
    AMIBERRY_BATOCERA_SYSTEM=lePotato
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_ORANGEPI_ZERO2),y)
    AMIBERRY_BATOCERA_SYSTEM=a64
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RK3326),y)
	AMIBERRY_BATOCERA_SYSTEM=oga
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RK3399),y)
	AMIBERRY_BATOCERA_SYSTEM=lePotato
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RK3288),y)
	AMIBERRY_BATOCERA_SYSTEM=RK3288
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RK3588),y)
	AMIBERRY_BATOCERA_SYSTEM=RK3588
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_S905),y)
	AMIBERRY_BATOCERA_SYSTEM=AMLGXBB
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_S905GEN2),y)
	AMIBERRY_BATOCERA_SYSTEM=a64
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_S905GEN3),y)
	AMIBERRY_BATOCERA_SYSTEM=AMLSM1
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_S912),y)
	AMIBERRY_BATOCERA_SYSTEM=AMLGXM
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_ORANGEPI_PC),y)
	AMIBERRY_BATOCERA_SYSTEM=orangepi-pc
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_CHA),y)
	AMIBERRY_BATOCERA_SYSTEM=orangepi-pc
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_S812),y)
    AMIBERRY_BATOCERA_SYSTEM=s812
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RK3328),y)
	AMIBERRY_BATOCERA_SYSTEM=AMLGXBB
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RK3128),y)
	AMIBERRY_BATOCERA_SYSTEM=orangepi-pc
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_ODIN),y)
	AMIBERRY_BATOCERA_SYSTEM=odin
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_ORANGEPI_3_LTS),y)
	AMIBERRY_BATOCERA_SYSTEM=a64
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
		LD="$(TARGET_LD)" \
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

define AMIBERRY_EVMAP
	mkdir -p $(TARGET_DIR)/usr/share/evmapy

	cp -prn $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulators/amiberry/controllers/amiga500.amiberry.keys \
		$(TARGET_DIR)/usr/share/evmapy
	cp -prn $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulators/amiberry/controllers/amiga1200.amiberry.keys \
		$(TARGET_DIR)/usr/share/evmapy
	cp -prn $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulators/amiberry/controllers/amigacd32.amiberry.keys \
		$(TARGET_DIR)/usr/share/evmapy
endef

AMIBERRY_POST_INSTALL_TARGET_HOOKS = AMIBERRY_EVMAP

$(eval $(generic-package))
