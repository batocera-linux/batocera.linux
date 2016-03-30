################################################################################
#
# kodi it_it language resource
#
################################################################################

KODI_RESOURCE_LANGUAGE_IT_IT_VERSION = 2.0.5
KODI_RESOURCE_LANGUAGE_IT_IT_SOURCE = resource.language.it_it-$(KODI_RESOURCE_LANGUAGE_IT_IT_VERSION).zip
KODI_RESOURCE_LANGUAGE_IT_IT_SITE = http://mirrors.kodi.tv/addons/jarvis/resource.language.it_it
KODI_RESOURCE_LANGUAGE_IT_IT_PLUGINNAME=resource.language.it_it

KODI_PLUGIN_TARGET_DIR=$(TARGET_DIR)/usr/share/kodi/addons

define KODI_RESOURCE_LANGUAGE_IT_IT_EXTRACT_CMDS
	@unzip -q -o $(DL_DIR)/$(KODI_RESOURCE_LANGUAGE_IT_IT_SOURCE) -d $(@D)
endef

define KODI_RESOURCE_LANGUAGE_IT_IT_INSTALL_TARGET_CMDS
	@mkdir -p $(KODI_PLUGIN_TARGET_DIR)
	@cp -r $(@D)/$(KODI_RESOURCE_LANGUAGE_IT_IT_PLUGINNAME) $(KODI_PLUGIN_TARGET_DIR)
endef

$(eval $(generic-package))
