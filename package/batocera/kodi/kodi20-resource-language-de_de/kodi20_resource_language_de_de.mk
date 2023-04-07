################################################################################
#
# kodi20 de_de language resource
#
################################################################################

KODI20_RESOURCE_LANGUAGE_DE_DE_VERSION = 10.0.71
KODI20_RESOURCE_LANGUAGE_DE_DE_SOURCE = resource.language.de_de-$(KODI20_RESOURCE_LANGUAGE_DE_DE_VERSION).zip
KODI20_RESOURCE_LANGUAGE_DE_DE_SITE = http://mirrors.kodi.tv/addons/nexus/resource.language.de_de
KODI20_RESOURCE_LANGUAGE_DE_DE_PLUGINNAME=resource.language.de_de

KODI20_PLUGIN_TARGET_DIR=$(TARGET_DIR)/usr/share/kodi/addons

define KODI20_RESOURCE_LANGUAGE_DE_DE_EXTRACT_CMDS
	@unzip -q -o $(DL_DIR)/$(KODI20_RESOURCE_LANGUAGE_DE_DE_DL_SUBDIR)/$(KODI20_RESOURCE_LANGUAGE_DE_DE_SOURCE) -d $(@D)
endef

define KODI20_RESOURCE_LANGUAGE_DE_DE_INSTALL_TARGET_CMDS
	@mkdir -p $(KODI20_PLUGIN_TARGET_DIR)
	@cp -r $(@D)/$(KODI20_RESOURCE_LANGUAGE_DE_DE_PLUGINNAME) $(KODI20_PLUGIN_TARGET_DIR)
endef

$(eval $(generic-package))
