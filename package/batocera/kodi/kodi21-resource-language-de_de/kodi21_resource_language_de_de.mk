################################################################################
#
# kodi21 de_de language resource
#
################################################################################

KODI21_RESOURCE_LANGUAGE_DE_DE_VERSION = 11.0.98
KODI21_RESOURCE_LANGUAGE_DE_DE_SOURCE = \
    resource.language.de_de-$(KODI21_RESOURCE_LANGUAGE_DE_DE_VERSION).zip
KODI21_RESOURCE_LANGUAGE_DE_DE_SITE = \
    https://mirrors.kodi.tv/addons/omega/resource.language.de_de
KODI21_RESOURCE_LANGUAGE_DE_DE_PLUGINNAME=resource.language.de_de

KODI21_PLUGIN_TARGET_DIR=$(TARGET_DIR)/usr/share/kodi/addons

define KODI21_RESOURCE_LANGUAGE_DE_DE_EXTRACT_CMDS
	@unzip -q -o \
	$(DL_DIR)/$(KODI21_RESOURCE_LANGUAGE_DE_DE_DL_SUBDIR)/$(KODI21_RESOURCE_LANGUAGE_DE_DE_SOURCE) \
	    -d $(@D)
endef

define KODI21_RESOURCE_LANGUAGE_DE_DE_INSTALL_TARGET_CMDS
	@mkdir -p $(KODI21_PLUGIN_TARGET_DIR)
	@cp -r $(@D)/$(KODI21_RESOURCE_LANGUAGE_DE_DE_PLUGINNAME) \
	    $(KODI21_PLUGIN_TARGET_DIR)
endef

$(eval $(generic-package))
