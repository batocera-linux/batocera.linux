################################################################################
#
# kodi20 it_it language resource
#
################################################################################

KODI20_RESOURCE_LANGUAGE_IT_IT_VERSION = 10.0.67
KODI20_RESOURCE_LANGUAGE_IT_IT_SOURCE = resource.language.it_it-$(KODI20_RESOURCE_LANGUAGE_IT_IT_VERSION).zip
KODI20_RESOURCE_LANGUAGE_IT_IT_SITE = http://mirrors.kodi.tv/addons/nexus/resource.language.it_it
KODI20_RESOURCE_LANGUAGE_IT_IT_PLUGINNAME=resource.language.it_it

KODI20_PLUGIN_TARGET_DIR=$(TARGET_DIR)/usr/share/kodi/addons

define KODI20_RESOURCE_LANGUAGE_IT_IT_EXTRACT_CMDS
	@unzip -q -o $(DL_DIR)/$(KODI20_RESOURCE_LANGUAGE_IT_IT_DL_SUBDIR)/$(KODI20_RESOURCE_LANGUAGE_IT_IT_SOURCE) -d $(@D)
endef

define KODI20_RESOURCE_LANGUAGE_IT_IT_INSTALL_TARGET_CMDS
	@mkdir -p $(KODI20_PLUGIN_TARGET_DIR)
	@cp -r $(@D)/$(KODI20_RESOURCE_LANGUAGE_IT_IT_PLUGINNAME) $(KODI20_PLUGIN_TARGET_DIR)
endef

$(eval $(generic-package))
