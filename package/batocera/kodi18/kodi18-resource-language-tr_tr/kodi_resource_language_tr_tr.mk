################################################################################
#
# kodi tr_tr language resource
#
################################################################################

KODI18_RESOURCE_LANGUAGE_TR_TR_VERSION = 9.0.14
KODI18_RESOURCE_LANGUAGE_TR_TR_SOURCE = resource.language.tr_tr-$(KODI18_RESOURCE_LANGUAGE_TR_TR_VERSION).zip
KODI18_RESOURCE_LANGUAGE_TR_TR_SITE = http://mirrors.kodi.tv/addons/leia/resource.language.tr_tr
KODI18_RESOURCE_LANGUAGE_TR_TR_PLUGINNAME=resource.language.tr_tr

KODI18_PLUGIN_TARGET_DIR=$(TARGET_DIR)/usr/share/kodi/addons

define KODI18_RESOURCE_LANGUAGE_TR_TR_EXTRACT_CMDS
	@unzip -q -o $(DL_DIR)/$(KODI18_RESOURCE_LANGUAGE_TR_TR_DL_SUBDIR)/$(KODI18_RESOURCE_LANGUAGE_TR_TR_SOURCE) -d $(@D)
endef

define KODI18_RESOURCE_LANGUAGE_TR_TR_INSTALL_TARGET_CMDS
	@mkdir -p $(KODI18_PLUGIN_TARGET_DIR)
	@cp -r $(@D)/$(KODI18_RESOURCE_LANGUAGE_TR_TR_PLUGINNAME) $(KODI18_PLUGIN_TARGET_DIR)
endef

$(eval $(generic-package))
