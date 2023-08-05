################################################################################
#
# kodi20 pt_br language resource
#
################################################################################

KODI20_RESOURCE_LANGUAGE_PT_BR_VERSION = 10.0.69
KODI20_RESOURCE_LANGUAGE_PT_BR_SOURCE = resource.language.pt_br-$(KODI20_RESOURCE_LANGUAGE_PT_BR_VERSION).zip
KODI20_RESOURCE_LANGUAGE_PT_BR_SITE = http://mirrors.kodi.tv/addons/nexus/resource.language.pt_br
KODI20_RESOURCE_LANGUAGE_PT_BR_PLUGINNAME=resource.language.pt_br

KODI20_PLUGIN_TARGET_DIR=$(TARGET_DIR)/usr/share/kodi/addons

define KODI20_RESOURCE_LANGUAGE_PT_BR_EXTRACT_CMDS
	@unzip -q -o $(DL_DIR)/$(KODI20_RESOURCE_LANGUAGE_PT_BR_DL_SUBDIR)/$(KODI20_RESOURCE_LANGUAGE_PT_BR_SOURCE) -d $(@D)
endef

define KODI20_RESOURCE_LANGUAGE_PT_BR_INSTALL_TARGET_CMDS
	@mkdir -p $(KODI20_PLUGIN_TARGET_DIR)
	@cp -r $(@D)/$(KODI20_RESOURCE_LANGUAGE_PT_BR_PLUGINNAME) $(KODI20_PLUGIN_TARGET_DIR)
endef

$(eval $(generic-package))
