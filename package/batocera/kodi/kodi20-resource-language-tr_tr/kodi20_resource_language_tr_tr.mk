################################################################################
#
# kodi20 tr_tr language resource
#
################################################################################

KODI20_RESOURCE_LANGUAGE_TR_TR_VERSION = 10.0.64
KODI20_RESOURCE_LANGUAGE_TR_TR_SOURCE = resource.language.tr_tr-$(KODI20_RESOURCE_LANGUAGE_TR_TR_VERSION).zip
KODI20_RESOURCE_LANGUAGE_TR_TR_SITE = http://mirrors.kodi.tv/addons/nexus/resource.language.tr_tr
KODI20_RESOURCE_LANGUAGE_TR_TR_PLUGINNAME=resource.language.tr_tr

KODI20_PLUGIN_TARGET_DIR=$(TARGET_DIR)/usr/share/kodi/addons

define KODI20_RESOURCE_LANGUAGE_TR_TR_EXTRACT_CMDS
	@unzip -q -o $(DL_DIR)/$(KODI20_RESOURCE_LANGUAGE_TR_TR_DL_SUBDIR)/$(KODI20_RESOURCE_LANGUAGE_TR_TR_SOURCE) -d $(@D)
endef

define KODI20_RESOURCE_LANGUAGE_TR_TR_INSTALL_TARGET_CMDS
	@mkdir -p $(KODI20_PLUGIN_TARGET_DIR)
	@cp -r $(@D)/$(KODI20_RESOURCE_LANGUAGE_TR_TR_PLUGINNAME) $(KODI20_PLUGIN_TARGET_DIR)
endef

$(eval $(generic-package))
