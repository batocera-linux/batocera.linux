################################################################################
#
# demul
#
################################################################################
# version: DEmul x86 v0.7 BUILD 251220 - closed source
DEMUL_VERSION = demul_251220
DEMUL_SOURCE = $(DEMUL_VERSION).7z
DEMUL_SITE = $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulators/demul
DEMUL_SITE_METHOD = file

DEMUL_DEPENDENCIES = xdotool
DEMUL_EXTRACT_DEPENDENCIES = host-p7zip

$(eval $(call register,demul.emulator.yml))

define DEMUL_EXTRACT_CMDS
	mkdir -p $(@D) && cd $(@D) && $(HOST_DIR)/usr/bin/7zr x -y \
	    $(DL_DIR)/$(DEMUL_DL_SUBDIR)/$(DEMUL_SOURCE)
endef

define DEMUL_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/usr
	cp -pr $(@D) $(TARGET_DIR)/usr/demul

    # copy evmapy configs
	mkdir -p $(TARGET_DIR)/usr/share/evmapy
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulators/demul/*.keys \
	    $(TARGET_DIR)/usr/share/evmapy

	# copy modified pad ini file for 2 players
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulators/demul/padDemul.ini \
	    $(TARGET_DIR)/usr/demul/
endef

$(eval $(generic-package))
$(eval $(emulator-info-package))
