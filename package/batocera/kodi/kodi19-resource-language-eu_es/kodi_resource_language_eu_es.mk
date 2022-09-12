################################################################################
#
# kodi eu_es language resource
#
################################################################################

KODI19_RESOURCE_LANGUAGE_EU_ES_VERSION = 9.0.31
KODI19_RESOURCE_LANGUAGE_EU_ES_SOURCE = resource.language.eu_es-$(KODI19_RESOURCE_LANGUAGE_EU_ES_VERSION).zip
KODI19_RESOURCE_LANGUAGE_EU_ES_SITE = http://mirrors.kodi.tv/addons/matrix/resource.language.eu_es
KODI19_RESOURCE_LANGUAGE_EU_ES_PLUGINNAME=resource.language.eu_es

KODI19_PLUGIN_TARGET_DIR=$(TARGET_DIR)/usr/share/kodi/addons

define KODI19_RESOURCE_LANGUAGE_EU_ES_EXTRACT_CMDS
	@unzip -q -o $(DL_DIR)/$(KODI19_RESOURCE_LANGUAGE_EU_ES_DL_SUBDIR)/$(KODI19_RESOURCE_LANGUAGE_EU_ES_SOURCE) -d $(@D)
endef

define KODI19_RESOURCE_LANGUAGE_EU_ES_INSTALL_TARGET_CMDS
	@mkdir -p $(KODI19_PLUGIN_TARGET_DIR)
	@cp -r $(@D)/$(KODI19_RESOURCE_LANGUAGE_EU_ES_PLUGINNAME) $(KODI19_PLUGIN_TARGET_DIR)
endef

$(eval $(generic-package))
