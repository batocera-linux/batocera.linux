################################################################################
#
# batocera-shaders
#
################################################################################

BATOCERA_SHADERS_VERSION = 1.0
BATOCERA_SHADERS_SOURCE=
BATOCERA_SHADERS_DEPENDENCIES= common-shaders glsl-shaders slang-shaders

BATOCERA_SHADERS_DIRIN=$(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulators/retroarch/shaders/batocera-shaders/configs

ifeq ($(BATOCERA_GPU),x86)
	BATOCERA_SHADERS_SETS=sharp-bilinear-simple retro scanlines enhanced curvature zfast flatten-glow mega-bezel mega-bezel-lite mega-bezel-ultralite
else
	BATOCERA_SHADERS_SETS=sharp-bilinear-simple retro scanlines enhanced curvature zfast flatten-glow
endif

define BATOCERA_SHADERS_INSTALL_TARGET_CMDS
    mkdir -p $(TARGET_DIR)/usr/share/batocera/shaders/bezel/Mega_Bezel/Presets
	cp -R $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulators/retroarch/shaders/batocera-shaders/presets-batocera/* \
	    $(TARGET_DIR)/usr/share/batocera/shaders/bezel/Mega_Bezel/Presets

	# general
    mkdir -p $(TARGET_DIR)/usr/share/batocera/shaders/configs
	cp $(BATOCERA_SHADERS_DIRIN)/rendering-defaults.yml \
	    $(TARGET_DIR)/usr/share/batocera/shaders/configs/
	if test -e $(BATOCERA_SHADERS_DIRIN)/rendering-defaults-$(BATOCERA_GPU).yml; then \
		cp $(BATOCERA_SHADERS_DIRIN)/rendering-defaults-$(BATOCERA_GPU).yml \
		    $(TARGET_DIR)/usr/share/batocera/shaders/configs/rendering-defaults-arch.yml; \
	fi

	# sets
	for set in $(BATOCERA_SHADERS_SETS); do \
		mkdir -p $(TARGET_DIR)/usr/share/batocera/shaders/configs/$$set; \
		cp $(BATOCERA_SHADERS_DIRIN)/$$set/rendering-defaults.yml \
		    $(TARGET_DIR)/usr/share/batocera/shaders/configs/$$set/; \
		if test -e $(BATOCERA_SHADERS_DIRIN)/$$set/rendering-defaults-$(BATOCERA_GPU).yml; then \
			cp $(BATOCERA_SHADERS_DIRIN)/$$set/rendering-defaults-$(BATOCERA_GPU).yml \
			    $(TARGET_DIR)/usr/share/batocera/shaders/configs/$$set/rendering-defaults-arch.yml; \
		fi \
	done
endef

$(eval $(generic-package))
