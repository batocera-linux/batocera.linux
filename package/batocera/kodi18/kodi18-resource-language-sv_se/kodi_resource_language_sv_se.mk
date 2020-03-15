################################################################################
#
# kodi sv_se language resource
#
################################################################################

KODI18_RESOURCE_LANGUAGE_SV_SE_VERSION = 9.0.19
KODI18_RESOURCE_LANGUAGE_SV_SE_SOURCE = resource.language.sv_se-$(KODI18_RESOURCE_LANGUAGE_SV_SE_VERSION).zip
KODI18_RESOURCE_LANGUAGE_SV_SE_SITE = http://mirrors.kodi.tv/addons/leia/resource.language.sv_se
KODI18_RESOURCE_LANGUAGE_SV_SE_PLUGINNAME=resource.language.sv_se

KODI18_PLUGIN_TARGET_DIR=$(TARGET_DIR)/usr/share/kodi/addons

define KODI18_RESOURCE_LANGUAGE_SV_SE_EXTRACT_CMDS
	@unzip -q -o $(DL_DIR)/$(KODI18_RESOURCE_LANGUAGE_SV_SE_DL_SUBDIR)/$(KODI18_RESOURCE_LANGUAGE_SV_SE_SOURCE) -d $(@D)
endef

define KODI18_RESOURCE_LANGUAGE_SV_SE_INSTALL_TARGET_CMDS
	@mkdir -p $(KODI18_PLUGIN_TARGET_DIR)
	@cp -r $(@D)/$(KODI18_RESOURCE_LANGUAGE_SV_SE_PLUGINNAME) $(KODI18_PLUGIN_TARGET_DIR)
endef

$(eval $(generic-package))
