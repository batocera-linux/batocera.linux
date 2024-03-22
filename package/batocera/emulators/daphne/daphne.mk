################################################################################
#
# hypseus-singe - aka # daphne
#
################################################################################

DAPHNE_VERSION = v2.11.1
DAPHNE_SITE = https://github.com/DirtBagXon/hypseus-singe
DAPHNE_SITE_METHOD=git
DAPHNE_LICENSE = GPLv3
DAPHNE_DEPENDENCIES = sdl2 sdl2_image sdl2_ttf zlib libogg libvorbis libmpeg2

DAPHNE_BEZELS_SOURCE = Bezels_Pack.zip
DAPHNE_EXTRA_DOWNLOADS = \
    $(DAPHNE_SITE)/releases/download/$(DAPHNE_VERSION)/$(DAPHNE_BEZELS_SOURCE)

DAPHNE_SUBDIR = build
DAPHNE_CONF_OPTS = ../src -DBUILD_SHARED_LIBS=OFF

define DAPHNE_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/build/hypseus $(TARGET_DIR)/usr/bin/
		mkdir -p $(TARGET_DIR)/usr/share/daphne
	
	# copy support files
	cp -pr $(@D)/pics $(TARGET_DIR)/usr/share/daphne
	cp -pr $(@D)/fonts $(TARGET_DIR)/usr/share/daphne
	cp -pr $(@D)/sound $(TARGET_DIR)/usr/share/daphne
	cp -pf $(@D)/doc/*.ini $(TARGET_DIR)/usr/share/daphne

	#evmap config
	mkdir -p $(TARGET_DIR)/usr/share/evmapy
	cp -prn $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulators/daphne/daphne.daphne.keys \
	    $(TARGET_DIR)/usr/share/evmapy
endef

define DAPHNE_INSTALL_BEZELS
    mkdir -p $(@D)/bezels
    cd $(@D)/bezels && unzip -x -o $(DL_DIR)/$(DAPHNE_DL_SUBDIR)/$(DAPHNE_BEZELS_SOURCE)
	mkdir -p $(TARGET_DIR)/usr/share/daphne/bezels
	cp -f $(@D)/bezels/daphne/Daphne.png $(TARGET_DIR)/usr/share/daphne/bezels
	cp -f $(@D)/bezels/daphne/v2/*.png $(TARGET_DIR)/usr/share/daphne/bezels
	cp -f $(@D)/bezels/singe/*.png $(TARGET_DIR)/usr/share/daphne/bezels
	cp -f $(@D)/bezels/singe/gungames/*.png $(TARGET_DIR)/usr/share/daphne/bezels
	cp -f $(@D)/bezels/singe/gungames/actionmax/*.png $(TARGET_DIR)/usr/share/daphne/bezels
	# Sinden
	mkdir -p $(TARGET_DIR)/usr/share/daphne/bezels/sinden
	cp -f $(@D)/bezels/singe/sinden/actionmax/*.png $(TARGET_DIR)/usr/share/daphne/bezels/sinden
	cp -f $(@D)/bezels/singe/sinden/original/*.png $(TARGET_DIR)/usr/share/daphne/bezels/sinden
	cp -f $(@D)/bezels/singe/sinden/shaded/*.png $(TARGET_DIR)/usr/share/daphne/bezels/sinden
endef

# Extract the bezels we want
DAPHNE_POST_INSTALL_TARGET_HOOKS = DAPHNE_INSTALL_BEZELS

$(eval $(cmake-package))
