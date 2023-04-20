################################################################################
#
# kodi20 eu_es language resource
#
################################################################################

KODI20_RESOURCE_LANGUAGE_EU_ES_VERSION = 10.0.49
KODI20_RESOURCE_LANGUAGE_EU_ES_SOURCE = resource.language.eu_es-$(KODI20_RESOURCE_LANGUAGE_EU_ES_VERSION).zip
KODI20_RESOURCE_LANGUAGE_EU_ES_SITE = http://mirrors.kodi.tv/addons/nexus/resource.language.eu_es
KODI20_RESOURCE_LANGUAGE_EU_ES_PLUGINNAME=resource.language.eu_es

KODI20_PLUGIN_TARGET_DIR=$(TARGET_DIR)/usr/share/kodi/addons

define KODI20_RESOURCE_LANGUAGE_EU_ES_EXTRACT_CMDS
	@unzip -q -o $(DL_DIR)/$(KODI20_RESOURCE_LANGUAGE_EU_ES_DL_SUBDIR)/$(KODI20_RESOURCE_LANGUAGE_EU_ES_SOURCE) -d $(@D)
endef

define KODI20_RESOURCE_LANGUAGE_EU_ES_INSTALL_TARGET_CMDS
	@mkdir -p $(KODI20_PLUGIN_TARGET_DIR)
	@cp -r $(@D)/$(KODI20_RESOURCE_LANGUAGE_EU_ES_PLUGINNAME) $(KODI20_PLUGIN_TARGET_DIR)
endef

$(eval $(generic-package))
