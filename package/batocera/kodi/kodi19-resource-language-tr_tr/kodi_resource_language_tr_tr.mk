################################################################################
#
# kodi tr_tr language resource
#
################################################################################

KODI19_RESOURCE_LANGUAGE_TR_TR_VERSION = 9.0.37
KODI19_RESOURCE_LANGUAGE_TR_TR_SOURCE = resource.language.tr_tr-$(KODI19_RESOURCE_LANGUAGE_TR_TR_VERSION).zip
KODI19_RESOURCE_LANGUAGE_TR_TR_SITE = http://mirrors.kodi.tv/addons/matrix/resource.language.tr_tr
KODI19_RESOURCE_LANGUAGE_TR_TR_PLUGINNAME=resource.language.tr_tr

KODI19_PLUGIN_TARGET_DIR=$(TARGET_DIR)/usr/share/kodi/addons

define KODI19_RESOURCE_LANGUAGE_TR_TR_EXTRACT_CMDS
	@unzip -q -o $(DL_DIR)/$(KODI19_RESOURCE_LANGUAGE_TR_TR_DL_SUBDIR)/$(KODI19_RESOURCE_LANGUAGE_TR_TR_SOURCE) -d $(@D)
endef

define KODI19_RESOURCE_LANGUAGE_TR_TR_INSTALL_TARGET_CMDS
	@mkdir -p $(KODI19_PLUGIN_TARGET_DIR)
	@cp -r $(@D)/$(KODI19_RESOURCE_LANGUAGE_TR_TR_PLUGINNAME) $(KODI19_PLUGIN_TARGET_DIR)
endef

$(eval $(generic-package))
