################################################################################
#
# kodi pt_br language resource
#
################################################################################

KODI19_RESOURCE_LANGUAGE_PT_BR_VERSION = 9.0.34
KODI19_RESOURCE_LANGUAGE_PT_BR_SOURCE = resource.language.pt_br-$(KODI19_RESOURCE_LANGUAGE_PT_BR_VERSION).zip
KODI19_RESOURCE_LANGUAGE_PT_BR_SITE = http://mirrors.kodi.tv/addons/matrix/resource.language.pt_br
KODI19_RESOURCE_LANGUAGE_PT_BR_PLUGINNAME=resource.language.pt_br

KODI19_PLUGIN_TARGET_DIR=$(TARGET_DIR)/usr/share/kodi/addons

define KODI19_RESOURCE_LANGUAGE_PT_BR_EXTRACT_CMDS
	@unzip -q -o $(DL_DIR)/$(KODI19_RESOURCE_LANGUAGE_PT_BR_DL_SUBDIR)/$(KODI19_RESOURCE_LANGUAGE_PT_BR_SOURCE) -d $(@D)
endef

define KODI19_RESOURCE_LANGUAGE_PT_BR_INSTALL_TARGET_CMDS
	@mkdir -p $(KODI19_PLUGIN_TARGET_DIR)
	@cp -r $(@D)/$(KODI19_RESOURCE_LANGUAGE_PT_BR_PLUGINNAME) $(KODI19_PLUGIN_TARGET_DIR)
endef

$(eval $(generic-package))
