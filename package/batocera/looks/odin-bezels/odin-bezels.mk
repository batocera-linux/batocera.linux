################################################################################
#
# odin-bezels
#
################################################################################

ODIN_BEZELS_VERSION = v0.1.1
ODIN_BEZELS_SITE = https://github.com/Tovarichtch/Odin/releases/download/$(ODIN_BEZELS_VERSION)
ODIN_BEZELS_SOURCE = Odin-Artwork.zip
ODIN_BEZELS_LICENSE = Proprietary
ODIN_BEZELS_LICENSE_FILES = artwork/NOTICE.txt

ODIN_BEZELS_DEPENDENCIES = odin

define ODIN_BEZELS_EXTRACT_CMDS
	$(UNZIP) -d $(@D) $(ODIN_BEZELS_DL_DIR)/$(ODIN_BEZELS_SOURCE)
endef

define ODIN_BEZELS_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/usr/share/odin/artwork
	cp -f $(@D)/artwork/*_bezel.png $(@D)/artwork/*_bezel.info $(TARGET_DIR)/usr/share/odin/artwork
endef

$(eval $(generic-package))
