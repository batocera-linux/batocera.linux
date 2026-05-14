################################################################################
#
# amiberry
#
################################################################################

AMIBERRY_VERSION = v8.1.5
AMIBERRY_SITE = $(call github,BlitterStudio,amiberry,$(AMIBERRY_VERSION))
AMIBERRY_LICENSE = GPLv3
AMIBERRY_SUPPORTS_IN_SOURCE_BUILD = NO

AMIBERRY_DEPENDENCIES += sdl3 sdl3_image sdl3_ttf mpg123 libpcap libxml2 libmpeg2 libcurl json-for-modern-cpp
AMIBERRY_DEPENDENCIES += flac libpng libserialport libportmidi libzlib libenet
AMIBERRY_EMULATOR_INFO = amiberry.emulator.yml

AMIBERRY_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release
AMIBERRY_CONF_OPTS += -DWITH_LTO=ON

ifeq ($(BR2_PACKAGE_LIBGLEW)$(BR2_PACKAGE_LIBGLU),yy)
AMIBERRY_DEPENDENCIES += libglew libglu
AMIBERRY_CONF_OPTS += -DUSE_OPENGL=ON
else
AMIBERRY_CONF_OPTS += -DUSE_OPENGL=OFF
endif

define AMIBERRY_INSTALL_TARGET_CMDS
	# install binary
	$(INSTALL) -D $(@D)/buildroot-build/amiberry $(TARGET_DIR)/usr/bin/amiberry

	# Copy AROS (open source alternative BIOS)
	mkdir -p $(TARGET_DIR)/usr/share/batocera/datainit/bios/amiga
	cp -prn $(@D)/buildroot-build/roms/aros-ext.bin \
	    $(TARGET_DIR)/usr/share/batocera/datainit/bios/amiga/
	cp -prn $(@D)/buildroot-build/roms/aros-rom.bin \
	    $(TARGET_DIR)/usr/share/batocera/datainit/bios/amiga/

	# Copy data and whdboot folders
	mkdir -p $(TARGET_DIR)/usr/share/amiberry
	cp -pr $(@D)/buildroot-build/whdboot $(TARGET_DIR)/usr/share/amiberry/
	cp -pr $(@D)/buildroot-build/data $(TARGET_DIR)/usr/share/amiberry/
endef

define AMIBERRY_EVMAP
	mkdir -p $(TARGET_DIR)/usr/share/evmapy
	cp -prn $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulators/amiberry/amiga500.amiberry.keys \
		$(TARGET_DIR)/usr/share/evmapy
	cp -prn $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulators/amiberry/amiga1200.amiberry.keys \
		$(TARGET_DIR)/usr/share/evmapy
	cp -prn $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulators/amiberry/amigacd32.amiberry.keys \
		$(TARGET_DIR)/usr/share/evmapy
	cp -prn $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulators/amiberry/amigacdtv.amiberry.keys \
		$(TARGET_DIR)/usr/share/evmapy
endef

AMIBERRY_POST_INSTALL_TARGET_HOOKS = AMIBERRY_EVMAP

$(eval $(cmake-package))
$(eval $(emulator-info-package))
