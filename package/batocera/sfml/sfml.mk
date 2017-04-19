################################################################################
#
# SFML - Simple and Fast Multimedia Library
#
################################################################################

SFML_VERSION = 2.4.0
SFML_SOURCE = SFML-$(SFML_VERSION)-sources.zip
SFML_SITE = http://www.sfml-dev.org/files
SFML_DEPENDENCIES = xcb-util-image openal jpeg flac

SFML_INSTALL_STAGING = YES

define SFML_EXTRACT_CMDS
	mkdir -p $(SFML_DIR)
	$(UNZIP) -d $(SFML_DIR)/ $(DL_DIR)/$(SFML_SOURCE)
	mv $(SFML_DIR)/SFML-$(SFML_VERSION)/* $(SFML_DIR)
	mv $(SFML_DIR)/SFML-$(SFML_VERSION)/.editorconfig $(SFML_DIR)
	rmdir $(SFML_DIR)/SFML-$(SFML_VERSION)
endef

$(eval $(cmake-package))
