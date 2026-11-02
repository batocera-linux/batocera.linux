################################################################################
#
# steamdeck-dsp
#
################################################################################

STEAMDECK_DSP_VERSION = 1.03-1
STEAMDECK_DSP_SOURCE = steamdeck-dsp-$(STEAMDECK_DSP_VERSION)-any.pkg.tar.zst
STEAMDECK_DSP_SITE = https://steamdeck-packages.steamos.cloud/archlinux-mirror/jupiter-main/os/x86_64
STEAMDECK_DSP_LICENSE = Proprietary

STEAMDECK_DSP_DEPENDENCIES = alsa-ucm-conf pipewire sound-open-firmware wireplumber

# arch package, no top level directory to strip
define STEAMDECK_DSP_EXTRACT_CMDS
	$(ZSTDCAT) $(STEAMDECK_DSP_DL_DIR)/$(STEAMDECK_DSP_SOURCE) | \
		$(TAR) -C $(@D) $(TAR_OPTIONS) -
endef

# valve's acp5x ucm needs their kernel, the lcd uses alsa-ucm-conf's
define STEAMDECK_DSP_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/lib/firmware/amd
	cp -r $(@D)/usr/lib/firmware/amd/* $(TARGET_DIR)/lib/firmware/amd/
	mkdir -p $(TARGET_DIR)/usr/share/alsa/ucm2/conf.d
	cp -r $(@D)/usr/share/alsa/ucm2/conf.d/sof-nau8821-max $(TARGET_DIR)/usr/share/alsa/ucm2/conf.d/
	mkdir -p $(TARGET_DIR)/usr/lib/lv2
	cp -r $(@D)/usr/lib/lv2/valve_deck_speakers.lv2 $(TARGET_DIR)/usr/lib/lv2/
	$(foreach model,jupiter galileo, \
		$(INSTALL) -D -m 0644 \
			$(@D)/usr/share/wireplumber/hardware-profiles/valve-$(model)/wireplumber.conf.d/alsa-card1.conf \
			$(TARGET_DIR)/usr/share/wireplumber/wireplumber.conf.d/51-steamdeck-$(model).conf$(sep))
endef

$(eval $(generic-package))
