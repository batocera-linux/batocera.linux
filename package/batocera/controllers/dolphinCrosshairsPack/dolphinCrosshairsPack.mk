################################################################################
#
# dolphinCrosshairsPack
#
################################################################################

DOLPHINCROSSHAIRSPACK_VERSION = 0f86d4e80813339b057a425198a3adc446658408
DOLPHINCROSSHAIRSPACK_SITE = $(call github,ProfgLX,Sinden-Dolphin-Accuracy-Inis,$(DOLPHINCROSSHAIRSPACK_VERSION))

define DOLPHINCROSSHAIRSPACK_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/usr/share
	cp -pr $(@D)/DolphinCrosshairsPack $(TARGET_DIR)/usr/share/
	rm $(TARGET_DIR)"/usr/share/DolphinCrosshairsPack/Readme Crosshair removal Pack.pdf"
endef

$(eval $(generic-package))
