################################################################################
#
# kodi zh_cn language resource
#
################################################################################

KODI_RESOURCE_LANGUAGE_ZH_CN_VERSION = 3.0.11
KODI_RESOURCE_LANGUAGE_ZH_CN_SOURCE = resource.language.zh_cn-$(KODI_RESOURCE_LANGUAGE_ZH_CN_VERSION).zip
KODI_RESOURCE_LANGUAGE_ZH_CN_SITE = http://mirrors.kodi.tv/addons/krypton/resource.language.zh_cn
KODI_RESOURCE_LANGUAGE_ZH_CN_PLUGINNAME=resource.language.zh_cn

KODI_PLUGIN_TARGET_DIR=$(TARGET_DIR)/usr/share/kodi/addons

define KODI_RESOURCE_LANGUAGE_ZH_CN_EXTRACT_CMDS
	@unzip -q -o $(DL_DIR)/$(KODI_RESOURCE_LANGUAGE_ZH_CN_SOURCE) -d $(@D)
endef

define KODI_RESOURCE_LANGUAGE_ZH_CN_INSTALL_TARGET_CMDS
	@mkdir -p $(KODI_PLUGIN_TARGET_DIR)
	@cp -r $(@D)/$(KODI_RESOURCE_LANGUAGE_ZH_CN_PLUGINNAME) $(KODI_PLUGIN_TARGET_DIR)
endef

$(eval $(generic-package))
