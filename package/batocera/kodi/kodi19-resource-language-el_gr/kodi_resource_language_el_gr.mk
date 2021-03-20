################################################################################
#
# kodi el_gr language resource
#
################################################################################

KODI19_RESOURCE_LANGUAGE_EL_GR_VERSION = 9.0.21
KODI19_RESOURCE_LANGUAGE_EL_GR_SOURCE = resource.language.el_gr-$(KODI19_RESOURCE_LANGUAGE_EL_GR_VERSION).zip
KODI19_RESOURCE_LANGUAGE_EL_GR_SITE = http://mirrors.kodi.tv/addons/matrix/resource.language.el_gr
KODI19_RESOURCE_LANGUAGE_EL_GR_PLUGINNAME=resource.language.el_gr

KODI19_PLUGIN_TARGET_DIR=$(TARGET_DIR)/usr/share/kodi/addons

define KODI19_RESOURCE_LANGUAGE_EL_GR_EXTRACT_CMDS
	@unzip -q -o $(DL_DIR)/$(KODI19_RESOURCE_LANGUAGE_EL_GR_DL_SUBDIR)/$(KODI19_RESOURCE_LANGUAGE_EL_GR_SOURCE) -d $(@D)
endef

define KODI19_RESOURCE_LANGUAGE_EL_GR_INSTALL_TARGET_CMDS
	@mkdir -p $(KODI19_PLUGIN_TARGET_DIR)
	@cp -r $(@D)/$(KODI19_RESOURCE_LANGUAGE_EL_GR_PLUGINNAME) $(KODI19_PLUGIN_TARGET_DIR)
endef

$(eval $(generic-package))
