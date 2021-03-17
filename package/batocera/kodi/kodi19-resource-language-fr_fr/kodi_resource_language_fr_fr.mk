################################################################################
#
# kodi fr_fr language resource
#
################################################################################

KODI19_RESOURCE_LANGUAGE_FR_FR_VERSION = 9.0.36
KODI19_RESOURCE_LANGUAGE_FR_FR_SOURCE = resource.language.fr_fr-$(KODI19_RESOURCE_LANGUAGE_FR_FR_VERSION).zip
KODI19_RESOURCE_LANGUAGE_FR_FR_SITE = http://mirrors.kodi.tv/addons/matrix/resource.language.fr_fr
KODI19_RESOURCE_LANGUAGE_FR_FR_PLUGINNAME=resource.language.fr_fr

KODI19_PLUGIN_TARGET_DIR=$(TARGET_DIR)/usr/share/kodi/addons

define KODI19_RESOURCE_LANGUAGE_FR_FR_EXTRACT_CMDS
	@unzip -q -o $(DL_DIR)/$(KODI19_RESOURCE_LANGUAGE_FR_FR_DL_SUBDIR)/$(KODI19_RESOURCE_LANGUAGE_FR_FR_SOURCE) -d $(@D)
endef

define KODI19_RESOURCE_LANGUAGE_FR_FR_INSTALL_TARGET_CMDS
	@mkdir -p $(KODI19_PLUGIN_TARGET_DIR)
	@cp -r $(@D)/$(KODI19_RESOURCE_LANGUAGE_FR_FR_PLUGINNAME) $(KODI19_PLUGIN_TARGET_DIR)
endef

$(eval $(generic-package))
