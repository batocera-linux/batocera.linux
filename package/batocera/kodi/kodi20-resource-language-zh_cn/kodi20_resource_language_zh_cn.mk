################################################################################
#
# kodi20 zh_cn language resource
#
################################################################################

KODI20_RESOURCE_LANGUAGE_ZH_CN_VERSION = 10.0.63
KODI20_RESOURCE_LANGUAGE_ZH_CN_SOURCE = resource.language.zh_cn-$(KODI20_RESOURCE_LANGUAGE_ZH_CN_VERSION).zip
KODI20_RESOURCE_LANGUAGE_ZH_CN_SITE = http://mirrors.kodi.tv/addons/nexus/resource.language.zh_cn
KODI20_RESOURCE_LANGUAGE_ZH_CN_PLUGINNAME=resource.language.zh_cn

KODI20_PLUGIN_TARGET_DIR=$(TARGET_DIR)/usr/share/kodi/addons

define KODI20_RESOURCE_LANGUAGE_ZH_CN_EXTRACT_CMDS
	@unzip -q -o $(DL_DIR)/$(KODI20_RESOURCE_LANGUAGE_ZH_CN_DL_SUBDIR)/$(KODI20_RESOURCE_LANGUAGE_ZH_CN_SOURCE) -d $(@D)
endef

define KODI20_RESOURCE_LANGUAGE_ZH_CN_INSTALL_TARGET_CMDS
	@mkdir -p $(KODI20_PLUGIN_TARGET_DIR)
	@cp -r $(@D)/$(KODI20_RESOURCE_LANGUAGE_ZH_CN_PLUGINNAME) $(KODI20_PLUGIN_TARGET_DIR)
endef

$(eval $(generic-package))
