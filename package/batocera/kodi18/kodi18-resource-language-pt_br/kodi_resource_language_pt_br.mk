################################################################################
#
# kodi pt_br language resource
#
################################################################################

KODI18_RESOURCE_LANGUAGE_PT_BR_VERSION = 9.0.25
KODI18_RESOURCE_LANGUAGE_PT_BR_SOURCE = resource.language.pt_br-$(KODI18_RESOURCE_LANGUAGE_PT_BR_VERSION).zip
KODI18_RESOURCE_LANGUAGE_PT_BR_SITE = http://mirrors.kodi.tv/addons/leia/resource.language.pt_br
KODI18_RESOURCE_LANGUAGE_PT_BR_PLUGINNAME=resource.language.pt_br

KODI18_PLUGIN_TARGET_DIR=$(TARGET_DIR)/usr/share/kodi/addons

define KODI18_RESOURCE_LANGUAGE_PT_BR_EXTRACT_CMDS
	@unzip -q -o $(DL_DIR)/$(KODI18_RESOURCE_LANGUAGE_PT_BR_DL_SUBDIR)/$(KODI18_RESOURCE_LANGUAGE_PT_BR_SOURCE) -d $(@D)
endef

define KODI18_RESOURCE_LANGUAGE_PT_BR_INSTALL_TARGET_CMDS
	@mkdir -p $(KODI18_PLUGIN_TARGET_DIR)
	@cp -r $(@D)/$(KODI18_RESOURCE_LANGUAGE_PT_BR_PLUGINNAME) $(KODI18_PLUGIN_TARGET_DIR)
endef

$(eval $(generic-package))
