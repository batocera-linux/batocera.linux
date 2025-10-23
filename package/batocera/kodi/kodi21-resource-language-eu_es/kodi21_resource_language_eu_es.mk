################################################################################
#
# kodi21 eu_es language resource
#
################################################################################

KODI21_RESOURCE_LANGUAGE_EU_ES_VERSION = 11.0.69
KODI21_RESOURCE_LANGUAGE_EU_ES_SOURCE = \
    resource.language.eu_es-$(KODI21_RESOURCE_LANGUAGE_EU_ES_VERSION).zip
KODI21_RESOURCE_LANGUAGE_EU_ES_SITE = \
    https://mirrors.kodi.tv/addons/omega/resource.language.eu_es
KODI21_RESOURCE_LANGUAGE_EU_ES_PLUGINNAME=resource.language.eu_es

KODI21_PLUGIN_TARGET_DIR=$(TARGET_DIR)/usr/share/kodi/addons

define KODI21_RESOURCE_LANGUAGE_EU_ES_EXTRACT_CMDS
	@unzip -q -o \
	$(DL_DIR)/$(KODI21_RESOURCE_LANGUAGE_EU_ES_DL_SUBDIR)/$(KODI21_RESOURCE_LANGUAGE_EU_ES_SOURCE) \
	    -d $(@D)
endef

define KODI21_RESOURCE_LANGUAGE_EU_ES_INSTALL_TARGET_CMDS
	@mkdir -p $(KODI21_PLUGIN_TARGET_DIR)
	@cp -r $(@D)/$(KODI21_RESOURCE_LANGUAGE_EU_ES_PLUGINNAME) \
	    $(KODI21_PLUGIN_TARGET_DIR)
endef

$(eval $(generic-package))
