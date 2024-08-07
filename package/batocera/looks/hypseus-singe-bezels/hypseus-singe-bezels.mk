################################################################################
#
# hypseus-singe-bezels
#
################################################################################

HYPSEUS_SINGE_BEZELS_VERSION = 7fd874c0d49b901e984d87afba73b57a8973c349
HYPSEUS_SINGE_BEZELS_SITE = \
    $(call github,Tovarichtch,hypseus_singe_daphne_bezels,$(HYPSEUS_SINGE_BEZELS_VERSION))
HYPSEUS_SINGE_BEZELS_LICENSE = LGPL-3.0
HYPSEUS_SINGE_BEZELS_LICENSE_FILES = LICENSE

HYPSEUS_SINGE_BEZELS_DEPENDENCIES = hypseus-singe ffmpeg-python

define HYPSEUS_SINGE_BEZELS_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/usr/share/hypseus-singe/bezels
	cp -f $(@D)/default.png $(TARGET_DIR)/usr/share/hypseus-singe/bezels
	cp -f $(@D)/Daphne/*.png $(TARGET_DIR)/usr/share/hypseus-singe/bezels
	cp -f $(@D)/Singe/*.png $(TARGET_DIR)/usr/share/hypseus-singe/bezels
	cp -f $(@D)/Kimmy/*.png $(TARGET_DIR)/usr/share/hypseus-singe/bezels  
endef

$(eval $(generic-package))
