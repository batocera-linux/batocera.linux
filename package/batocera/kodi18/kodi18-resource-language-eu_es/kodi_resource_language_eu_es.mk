################################################################################
#
# kodi eu_es language resource
#
################################################################################

KODI18_RESOURCE_LANGUAGE_EU_ES_VERSION = 9.0.13
KODI18_RESOURCE_LANGUAGE_EU_ES_SOURCE = resource.language.eu_es-$(KODI18_RESOURCE_LANGUAGE_EU_ES_VERSION).zip
KODI18_RESOURCE_LANGUAGE_EU_ES_SITE = http://mirrors.kodi.tv/addons/leia/resource.language.eu_es
KODI18_RESOURCE_LANGUAGE_EU_ES_PLUGINNAME=resource.language.eu_es

KODI18_PLUGIN_TARGET_DIR=$(TARGET_DIR)/usr/share/kodi/addons

define KODI18_RESOURCE_LANGUAGE_EU_ES_EXTRACT_CMDS
	@unzip -q -o $(DL_DIR)/$(KODI18_RESOURCE_LANGUAGE_EU_ES_DL_SUBDIR)/$(KODI18_RESOURCE_LANGUAGE_EU_ES_SOURCE) -d $(@D)
endef

define KODI18_RESOURCE_LANGUAGE_EU_ES_INSTALL_TARGET_CMDS
	@mkdir -p $(KODI18_PLUGIN_TARGET_DIR)
	@cp -r $(@D)/$(KODI18_RESOURCE_LANGUAGE_EU_ES_PLUGINNAME) $(KODI18_PLUGIN_TARGET_DIR)
endef

$(eval $(generic-package))
