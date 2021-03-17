################################################################################
#
# kodi it_it language resource
#
################################################################################

KODI19_RESOURCE_LANGUAGE_IT_IT_VERSION = 9.0.27
KODI19_RESOURCE_LANGUAGE_IT_IT_SOURCE = resource.language.it_it-$(KODI19_RESOURCE_LANGUAGE_IT_IT_VERSION).zip
KODI19_RESOURCE_LANGUAGE_IT_IT_SITE = http://mirrors.kodi.tv/addons/matrix/resource.language.it_it
KODI19_RESOURCE_LANGUAGE_IT_IT_PLUGINNAME=resource.language.it_it

KODI19_PLUGIN_TARGET_DIR=$(TARGET_DIR)/usr/share/kodi/addons

define KODI19_RESOURCE_LANGUAGE_IT_IT_EXTRACT_CMDS
	@unzip -q -o $(DL_DIR)/$(KODI19_RESOURCE_LANGUAGE_IT_IT_DL_SUBDIR)/$(KODI19_RESOURCE_LANGUAGE_IT_IT_SOURCE) -d $(@D)
endef

define KODI19_RESOURCE_LANGUAGE_IT_IT_INSTALL_TARGET_CMDS
	@mkdir -p $(KODI19_PLUGIN_TARGET_DIR)
	@cp -r $(@D)/$(KODI19_RESOURCE_LANGUAGE_IT_IT_PLUGINNAME) $(KODI19_PLUGIN_TARGET_DIR)
endef

$(eval $(generic-package))
