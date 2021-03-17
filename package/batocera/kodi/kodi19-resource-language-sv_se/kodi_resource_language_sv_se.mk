################################################################################
#
# kodi sv_se language resource
#
################################################################################

KODI19_RESOURCE_LANGUAGE_SV_SE_VERSION = 9.0.31
KODI19_RESOURCE_LANGUAGE_SV_SE_SOURCE = resource.language.sv_se-$(KODI19_RESOURCE_LANGUAGE_SV_SE_VERSION).zip
KODI19_RESOURCE_LANGUAGE_SV_SE_SITE = http://mirrors.kodi.tv/addons/matrix/resource.language.sv_se
KODI19_RESOURCE_LANGUAGE_SV_SE_PLUGINNAME=resource.language.sv_se

KODI19_PLUGIN_TARGET_DIR=$(TARGET_DIR)/usr/share/kodi/addons

define KODI19_RESOURCE_LANGUAGE_SV_SE_EXTRACT_CMDS
	@unzip -q -o $(DL_DIR)/$(KODI19_RESOURCE_LANGUAGE_SV_SE_DL_SUBDIR)/$(KODI19_RESOURCE_LANGUAGE_SV_SE_SOURCE) -d $(@D)
endef

define KODI19_RESOURCE_LANGUAGE_SV_SE_INSTALL_TARGET_CMDS
	@mkdir -p $(KODI19_PLUGIN_TARGET_DIR)
	@cp -r $(@D)/$(KODI19_RESOURCE_LANGUAGE_SV_SE_PLUGINNAME) $(KODI19_PLUGIN_TARGET_DIR)
endef

$(eval $(generic-package))
