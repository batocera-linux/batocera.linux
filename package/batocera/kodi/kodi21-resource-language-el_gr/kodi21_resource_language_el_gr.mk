################################################################################
#
# kodi21 el_gr language resource
#
################################################################################

KODI21_RESOURCE_LANGUAGE_EL_GR_VERSION = 11.0.72
KODI21_RESOURCE_LANGUAGE_EL_GR_SOURCE = \
    resource.language.el_gr-$(KODI21_RESOURCE_LANGUAGE_EL_GR_VERSION).zip
KODI21_RESOURCE_LANGUAGE_EL_GR_SITE = \
    https://mirrors.kodi.tv/addons/omega/resource.language.el_gr
KODI21_RESOURCE_LANGUAGE_EL_GR_PLUGINNAME=resource.language.el_gr

KODI21_PLUGIN_TARGET_DIR=$(TARGET_DIR)/usr/share/kodi/addons

define KODI21_RESOURCE_LANGUAGE_EL_GR_EXTRACT_CMDS
	@unzip -q -o \
	$(DL_DIR)/$(KODI21_RESOURCE_LANGUAGE_EL_GR_DL_SUBDIR)/$(KODI21_RESOURCE_LANGUAGE_EL_GR_SOURCE) \
	    -d $(@D)
endef

define KODI21_RESOURCE_LANGUAGE_EL_GR_INSTALL_TARGET_CMDS
	@mkdir -p $(KODI21_PLUGIN_TARGET_DIR)
	@cp -r $(@D)/$(KODI21_RESOURCE_LANGUAGE_EL_GR_PLUGINNAME) \
	    $(KODI21_PLUGIN_TARGET_DIR)
endef

$(eval $(generic-package))
