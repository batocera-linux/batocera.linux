################################################################################
#
# kodi zh_cn language resource
#
################################################################################

KODI19_RESOURCE_LANGUAGE_ZH_CN_VERSION = 9.0.39
KODI19_RESOURCE_LANGUAGE_ZH_CN_SOURCE = resource.language.zh_cn-$(KODI19_RESOURCE_LANGUAGE_ZH_CN_VERSION).zip
KODI19_RESOURCE_LANGUAGE_ZH_CN_SITE = http://mirrors.kodi.tv/addons/matrix/resource.language.zh_cn
KODI19_RESOURCE_LANGUAGE_ZH_CN_PLUGINNAME=resource.language.zh_cn

KODI19_PLUGIN_TARGET_DIR=$(TARGET_DIR)/usr/share/kodi/addons

define KODI19_RESOURCE_LANGUAGE_ZH_CN_EXTRACT_CMDS
	@unzip -q -o $(DL_DIR)/$(KODI19_RESOURCE_LANGUAGE_ZH_CN_DL_SUBDIR)/$(KODI19_RESOURCE_LANGUAGE_ZH_CN_SOURCE) -d $(@D)
endef

define KODI19_RESOURCE_LANGUAGE_ZH_CN_INSTALL_TARGET_CMDS
	@mkdir -p $(KODI19_PLUGIN_TARGET_DIR)
	@cp -r $(@D)/$(KODI19_RESOURCE_LANGUAGE_ZH_CN_PLUGINNAME) $(KODI19_PLUGIN_TARGET_DIR)
endef

$(eval $(generic-package))
