################################################################################
#
# kodi21 fr_fr language resource
#
################################################################################

KODI21_RESOURCE_LANGUAGE_FR_FR_VERSION = 11.0.84
KODI21_RESOURCE_LANGUAGE_FR_FR_SOURCE = resource.language.fr_fr-$(KODI21_RESOURCE_LANGUAGE_FR_FR_VERSION).zip
KODI21_RESOURCE_LANGUAGE_FR_FR_SITE = https://mirrors.kodi.tv/addons/omega/resource.language.fr_fr
KODI21_RESOURCE_LANGUAGE_FR_FR_PLUGINNAME=resource.language.fr_fr

KODI21_PLUGIN_TARGET_DIR=$(TARGET_DIR)/usr/share/kodi/addons

define KODI21_RESOURCE_LANGUAGE_FR_FR_EXTRACT_CMDS
	@unzip -q -o $(DL_DIR)/$(KODI21_RESOURCE_LANGUAGE_FR_FR_DL_SUBDIR)/$(KODI21_RESOURCE_LANGUAGE_FR_FR_SOURCE) -d $(@D)
endef

define KODI21_RESOURCE_LANGUAGE_FR_FR_INSTALL_TARGET_CMDS
	@mkdir -p $(KODI21_PLUGIN_TARGET_DIR)
	@cp -r $(@D)/$(KODI21_RESOURCE_LANGUAGE_FR_FR_PLUGINNAME) $(KODI21_PLUGIN_TARGET_DIR)
endef

$(eval $(generic-package))
