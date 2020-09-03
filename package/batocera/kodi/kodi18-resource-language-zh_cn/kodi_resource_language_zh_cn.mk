################################################################################
#
# kodi zh_cn language resource
#
################################################################################

KODI18_RESOURCE_LANGUAGE_ZH_CN_VERSION = 9.0.16
KODI18_RESOURCE_LANGUAGE_ZH_CN_SOURCE = resource.language.zh_cn-$(KODI18_RESOURCE_LANGUAGE_ZH_CN_VERSION).zip
KODI18_RESOURCE_LANGUAGE_ZH_CN_SITE = http://mirrors.kodi.tv/addons/leia/resource.language.zh_cn
KODI18_RESOURCE_LANGUAGE_ZH_CN_PLUGINNAME=resource.language.zh_cn

KODI18_PLUGIN_TARGET_DIR=$(TARGET_DIR)/usr/share/kodi/addons

define KODI18_RESOURCE_LANGUAGE_ZH_CN_EXTRACT_CMDS
	@unzip -q -o $(DL_DIR)/$(KODI18_RESOURCE_LANGUAGE_ZH_CN_DL_SUBDIR)/$(KODI18_RESOURCE_LANGUAGE_ZH_CN_SOURCE) -d $(@D)
endef

define KODI18_RESOURCE_LANGUAGE_ZH_CN_INSTALL_TARGET_CMDS
	@mkdir -p $(KODI18_PLUGIN_TARGET_DIR)
	@cp -r $(@D)/$(KODI18_RESOURCE_LANGUAGE_ZH_CN_PLUGINNAME) $(KODI18_PLUGIN_TARGET_DIR)
endef

$(eval $(generic-package))
