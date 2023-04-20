################################################################################
#
# kodi20 el_gr language resource
#
################################################################################

KODI20_RESOURCE_LANGUAGE_EL_GR_VERSION = 10.0.52
KODI20_RESOURCE_LANGUAGE_EL_GR_SOURCE = resource.language.el_gr-$(KODI20_RESOURCE_LANGUAGE_EL_GR_VERSION).zip
KODI20_RESOURCE_LANGUAGE_EL_GR_SITE = http://mirrors.kodi.tv/addons/nexus/resource.language.el_gr
KODI20_RESOURCE_LANGUAGE_EL_GR_PLUGINNAME=resource.language.el_gr

KODI20_PLUGIN_TARGET_DIR=$(TARGET_DIR)/usr/share/kodi/addons

define KODI20_RESOURCE_LANGUAGE_EL_GR_EXTRACT_CMDS
	@unzip -q -o $(DL_DIR)/$(KODI20_RESOURCE_LANGUAGE_EL_GR_DL_SUBDIR)/$(KODI20_RESOURCE_LANGUAGE_EL_GR_SOURCE) -d $(@D)
endef

define KODI20_RESOURCE_LANGUAGE_EL_GR_INSTALL_TARGET_CMDS
	@mkdir -p $(KODI20_PLUGIN_TARGET_DIR)
	@cp -r $(@D)/$(KODI20_RESOURCE_LANGUAGE_EL_GR_PLUGINNAME) $(KODI20_PLUGIN_TARGET_DIR)
endef

$(eval $(generic-package))
