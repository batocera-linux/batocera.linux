################################################################################
#
# kodi de_de language resource
#
################################################################################

KODI19_RESOURCE_LANGUAGE_DE_DE_VERSION = 9.0.49
KODI19_RESOURCE_LANGUAGE_DE_DE_SOURCE = resource.language.de_de-$(KODI19_RESOURCE_LANGUAGE_DE_DE_VERSION).zip
KODI19_RESOURCE_LANGUAGE_DE_DE_SITE = http://mirrors.kodi.tv/addons/matrix/resource.language.de_de
KODI19_RESOURCE_LANGUAGE_DE_DE_PLUGINNAME=resource.language.de_de

KODI19_PLUGIN_TARGET_DIR=$(TARGET_DIR)/usr/share/kodi/addons

define KODI19_RESOURCE_LANGUAGE_DE_DE_EXTRACT_CMDS
	@unzip -q -o $(DL_DIR)/$(KODI19_RESOURCE_LANGUAGE_DE_DE_DL_SUBDIR)/$(KODI19_RESOURCE_LANGUAGE_DE_DE_SOURCE) -d $(@D)
endef

define KODI19_RESOURCE_LANGUAGE_DE_DE_INSTALL_TARGET_CMDS
	@mkdir -p $(KODI19_PLUGIN_TARGET_DIR)
	@cp -r $(@D)/$(KODI19_RESOURCE_LANGUAGE_DE_DE_PLUGINNAME) $(KODI19_PLUGIN_TARGET_DIR)
endef

$(eval $(generic-package))
