################################################################################
#
# kodi it_it language resource
#
################################################################################

KODI18_RESOURCE_LANGUAGE_IT_IT_VERSION = 9.0.17
KODI18_RESOURCE_LANGUAGE_IT_IT_SOURCE = resource.language.it_it-$(KODI18_RESOURCE_LANGUAGE_IT_IT_VERSION).zip
KODI18_RESOURCE_LANGUAGE_IT_IT_SITE = http://mirrors.kodi.tv/addons/leia/resource.language.it_it
KODI18_RESOURCE_LANGUAGE_IT_IT_PLUGINNAME=resource.language.it_it

KODI18_PLUGIN_TARGET_DIR=$(TARGET_DIR)/usr/share/kodi/addons

define KODI18_RESOURCE_LANGUAGE_IT_IT_EXTRACT_CMDS
	@unzip -q -o $(DL_DIR)/$(KODI18_RESOURCE_LANGUAGE_IT_IT_DL_SUBDIR)/$(KODI18_RESOURCE_LANGUAGE_IT_IT_SOURCE) -d $(@D)
endef

define KODI18_RESOURCE_LANGUAGE_IT_IT_INSTALL_TARGET_CMDS
	@mkdir -p $(KODI18_PLUGIN_TARGET_DIR)
	@cp -r $(@D)/$(KODI18_RESOURCE_LANGUAGE_IT_IT_PLUGINNAME) $(KODI18_PLUGIN_TARGET_DIR)
endef

$(eval $(generic-package))
