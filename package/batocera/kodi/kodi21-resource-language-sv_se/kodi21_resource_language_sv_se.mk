################################################################################
#
# kodi21 sv_se language resource
#
################################################################################

KODI21_RESOURCE_LANGUAGE_SV_SE_VERSION = 11.0.90
KODI21_RESOURCE_LANGUAGE_SV_SE_SOURCE = \
    resource.language.sv_se-$(KODI21_RESOURCE_LANGUAGE_SV_SE_VERSION).zip
KODI21_RESOURCE_LANGUAGE_SV_SE_SITE = \
    https://mirrors.kodi.tv/addons/omega/resource.language.sv_se
KODI21_RESOURCE_LANGUAGE_SV_SE_PLUGINNAME=resource.language.sv_se

KODI21_PLUGIN_TARGET_DIR=$(TARGET_DIR)/usr/share/kodi/addons

define KODI21_RESOURCE_LANGUAGE_SV_SE_EXTRACT_CMDS
	@unzip -q -o \
	$(DL_DIR)/$(KODI21_RESOURCE_LANGUAGE_SV_SE_DL_SUBDIR)/$(KODI21_RESOURCE_LANGUAGE_SV_SE_SOURCE) \
	    -d $(@D)
endef

define KODI21_RESOURCE_LANGUAGE_SV_SE_INSTALL_TARGET_CMDS
	@mkdir -p $(KODI21_PLUGIN_TARGET_DIR)
	@cp -r $(@D)/$(KODI21_RESOURCE_LANGUAGE_SV_SE_PLUGINNAME) \
	    $(KODI21_PLUGIN_TARGET_DIR)
endef

$(eval $(generic-package))
