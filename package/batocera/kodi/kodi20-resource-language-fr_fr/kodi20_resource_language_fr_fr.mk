################################################################################
#
# kodi20 fr_fr language resource
#
################################################################################

KODI20_RESOURCE_LANGUAGE_FR_FR_VERSION = 10.0.75
KODI20_RESOURCE_LANGUAGE_FR_FR_SOURCE = resource.language.fr_fr-$(KODI20_RESOURCE_LANGUAGE_FR_FR_VERSION).zip
KODI20_RESOURCE_LANGUAGE_FR_FR_SITE = http://mirrors.kodi.tv/addons/nexus/resource.language.fr_fr
KODI20_RESOURCE_LANGUAGE_FR_FR_PLUGINNAME=resource.language.fr_fr

KODI20_PLUGIN_TARGET_DIR=$(TARGET_DIR)/usr/share/kodi/addons

define KODI20_RESOURCE_LANGUAGE_FR_FR_EXTRACT_CMDS
	@unzip -q -o $(DL_DIR)/$(KODI20_RESOURCE_LANGUAGE_FR_FR_DL_SUBDIR)/$(KODI20_RESOURCE_LANGUAGE_FR_FR_SOURCE) -d $(@D)
endef

define KODI20_RESOURCE_LANGUAGE_FR_FR_INSTALL_TARGET_CMDS
	@mkdir -p $(KODI20_PLUGIN_TARGET_DIR)
	@cp -r $(@D)/$(KODI20_RESOURCE_LANGUAGE_FR_FR_PLUGINNAME) $(KODI20_PLUGIN_TARGET_DIR)
endef

$(eval $(generic-package))
