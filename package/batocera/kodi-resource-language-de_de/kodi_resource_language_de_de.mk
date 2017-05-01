################################################################################
#
# kodi de_de language resource
#
################################################################################

KODI_RESOURCE_LANGUAGE_DE_DE_VERSION = 3.0.16
KODI_RESOURCE_LANGUAGE_DE_DE_SOURCE = resource.language.de_de-$(KODI_RESOURCE_LANGUAGE_DE_DE_VERSION).zip
KODI_RESOURCE_LANGUAGE_DE_DE_SITE = http://mirrors.kodi.tv/addons/krypton/resource.language.de_de
KODI_RESOURCE_LANGUAGE_DE_DE_PLUGINNAME=resource.language.de_de

KODI_PLUGIN_TARGET_DIR=$(TARGET_DIR)/usr/share/kodi/addons

define KODI_RESOURCE_LANGUAGE_DE_DE_EXTRACT_CMDS
	@unzip -q -o $(DL_DIR)/$(KODI_RESOURCE_LANGUAGE_DE_DE_SOURCE) -d $(@D)
endef

define KODI_RESOURCE_LANGUAGE_DE_DE_INSTALL_TARGET_CMDS
	@mkdir -p $(KODI_PLUGIN_TARGET_DIR)
	@cp -r $(@D)/$(KODI_RESOURCE_LANGUAGE_DE_DE_PLUGINNAME) $(KODI_PLUGIN_TARGET_DIR)
endef

$(eval $(generic-package))
