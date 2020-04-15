################################################################################
#
# kodi de_de language resource
#
################################################################################

KODI18_RESOURCE_LANGUAGE_DE_DE_VERSION = 9.0.21
KODI18_RESOURCE_LANGUAGE_DE_DE_SOURCE = resource.language.de_de-$(KODI18_RESOURCE_LANGUAGE_DE_DE_VERSION).zip
KODI18_RESOURCE_LANGUAGE_DE_DE_SITE = http://mirrors.kodi.tv/addons/leia/resource.language.de_de
KODI18_RESOURCE_LANGUAGE_DE_DE_PLUGINNAME=resource.language.de_de

KODI18_PLUGIN_TARGET_DIR=$(TARGET_DIR)/usr/share/kodi/addons

define KODI18_RESOURCE_LANGUAGE_DE_DE_EXTRACT_CMDS
	@unzip -q -o $(DL_DIR)/$(KODI18_RESOURCE_LANGUAGE_DE_DE_DL_SUBDIR)/$(KODI18_RESOURCE_LANGUAGE_DE_DE_SOURCE) -d $(@D)
endef

define KODI18_RESOURCE_LANGUAGE_DE_DE_INSTALL_TARGET_CMDS
	@mkdir -p $(KODI18_PLUGIN_TARGET_DIR)
	@cp -r $(@D)/$(KODI18_RESOURCE_LANGUAGE_DE_DE_PLUGINNAME) $(KODI18_PLUGIN_TARGET_DIR)
endef

$(eval $(generic-package))
