################################################################################
#
# kodi fr_fr language resource
#
################################################################################

KODI18_RESOURCE_LANGUAGE_FR_FR_VERSION = 9.0.24
KODI18_RESOURCE_LANGUAGE_FR_FR_SOURCE = resource.language.fr_fr-$(KODI18_RESOURCE_LANGUAGE_FR_FR_VERSION).zip
KODI18_RESOURCE_LANGUAGE_FR_FR_SITE = http://mirrors.kodi.tv/addons/leia/resource.language.fr_fr
KODI18_RESOURCE_LANGUAGE_FR_FR_PLUGINNAME=resource.language.fr_fr

KODI18_PLUGIN_TARGET_DIR=$(TARGET_DIR)/usr/share/kodi/addons

define KODI18_RESOURCE_LANGUAGE_FR_FR_EXTRACT_CMDS
	@unzip -q -o $(DL_DIR)/$(KODI18_RESOURCE_LANGUAGE_FR_FR_DL_SUBDIR)/$(KODI18_RESOURCE_LANGUAGE_FR_FR_SOURCE) -d $(@D)
endef

define KODI18_RESOURCE_LANGUAGE_FR_FR_INSTALL_TARGET_CMDS
	@mkdir -p $(KODI18_PLUGIN_TARGET_DIR)
	@cp -r $(@D)/$(KODI18_RESOURCE_LANGUAGE_FR_FR_PLUGINNAME) $(KODI18_PLUGIN_TARGET_DIR)
endef

$(eval $(generic-package))
