################################################################################
#
# hypseus-singe
#
################################################################################

HYPSEUS_SINGE_VERSION = v2.11.5
HYPSEUS_SINGE_SITE =  $(call github,DirtBagXon,hypseus-singe,$(HYPSEUS_SINGE_VERSION))
HYPSEUS_SINGE_LICENSE = GPLv3

HYPSEUS_SINGE_DEPENDENCIES += libmpeg2 libogg libvorbis libzip  
HYPSEUS_SINGE_DEPENDENCIES += sdl2 sdl2_image sdl2_mixer sdl2_ttf zlib

HYPSEUS_SINGE_SUBDIR = src

HYPSEUS_SINGE_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release
HYPSEUS_SINGE_CONF_OPTS += -DBUILD_SHARED_LIBS=OFF
HYPSEUS_SINGE_CONF_OPTS += -DABSTRACT_SINGE=OFF

define HYPSEUS_SINGE_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/src/hypseus $(TARGET_DIR)/usr/bin/
		mkdir -p $(TARGET_DIR)/usr/share/hypseus-singe
	
	# copy support files
	cp -pr $(@D)/pics $(TARGET_DIR)/usr/share/hypseus-singe
	cp -pr $(@D)/fonts $(TARGET_DIR)/usr/share/hypseus-singe
	cp -pr $(@D)/sound $(TARGET_DIR)/usr/share/hypseus-singe
	cp -pf $(@D)/doc/*.ini $(TARGET_DIR)/usr/share/hypseus-singe

	#evmap config
	mkdir -p $(TARGET_DIR)/usr/share/evmapy
	cp -f $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulators/hypseus-singe/*.keys \
	    $(TARGET_DIR)/usr/share/evmapy
endef

$(eval $(cmake-package))
