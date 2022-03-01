################################################################################
#
# demul
#
################################################################################

# version: DEmul x86 v0.7 BUILD 280418 - closed source
# not developed since 2018
DEMUL_VERSION = demul07_280418
DEMUL_SOURCE = $(DEMUL_VERSION).7z
DEMUL_SITE = http://demul.emulation64.com/files
DEMUL_DEPENDENCIES = host-p7zip

define DEMUL_EXTRACT_CMDS
	mkdir -p $(@D) && cd $(@D) && $(HOST_DIR)/usr/bin/7zr x -y $(DL_DIR)/$(DEMUL_DL_SUBDIR)/$(DEMUL_SOURCE)
endef

define DEMUL_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/usr
	cp -pr $(@D) $(TARGET_DIR)/usr/demul

    # copy english faq & evmap config
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulators/demul/faq_en.txt $(TARGET_DIR)/usr/demul/
	mkdir -p $(TARGET_DIR)/usr/share/evmapy
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulators/demul/*.keys $(TARGET_DIR)/usr/share/evmapy

	# copy modified pad ini file for 2 players
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulators/demul/padDemul.ini $(TARGET_DIR)/usr/demul/
endef

$(eval $(generic-package))
