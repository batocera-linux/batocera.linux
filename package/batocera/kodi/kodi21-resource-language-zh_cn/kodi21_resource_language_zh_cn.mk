################################################################################
#
# kodi21 zh_cn language resource
#
################################################################################

KODI21_RESOURCE_LANGUAGE_ZH_CN_VERSION = 11.0.90
KODI21_RESOURCE_LANGUAGE_ZH_CN_SOURCE = resource.language.zh_cn-$(KODI21_RESOURCE_LANGUAGE_ZH_CN_VERSION).zip
KODI21_RESOURCE_LANGUAGE_ZH_CN_SITE = https://mirrors.kodi.tv/addons/omega/resource.language.zh_cn
KODI21_RESOURCE_LANGUAGE_ZH_CN_PLUGINNAME=resource.language.zh_cn

KODI21_PLUGIN_TARGET_DIR=$(TARGET_DIR)/usr/share/kodi/addons

define KODI21_RESOURCE_LANGUAGE_ZH_CN_EXTRACT_CMDS
	@unzip -q -o $(DL_DIR)/$(KODI21_RESOURCE_LANGUAGE_ZH_CN_DL_SUBDIR)/$(KODI21_RESOURCE_LANGUAGE_ZH_CN_SOURCE) -d $(@D)
endef

define KODI21_RESOURCE_LANGUAGE_ZH_CN_INSTALL_TARGET_CMDS
	@mkdir -p $(KODI21_PLUGIN_TARGET_DIR)
	@cp -r $(@D)/$(KODI21_RESOURCE_LANGUAGE_ZH_CN_PLUGINNAME) $(KODI21_PLUGIN_TARGET_DIR)
endef

$(eval $(generic-package))
