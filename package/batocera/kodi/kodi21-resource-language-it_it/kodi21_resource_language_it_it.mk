################################################################################
#
# kodi21 it_it language resource
#
################################################################################

KODI21_RESOURCE_LANGUAGE_IT_IT_VERSION = 11.0.97
KODI21_RESOURCE_LANGUAGE_IT_IT_SOURCE = \
    resource.language.it_it-$(KODI21_RESOURCE_LANGUAGE_IT_IT_VERSION).zip
KODI21_RESOURCE_LANGUAGE_IT_IT_SITE = \
    https://mirrors.kodi.tv/addons/omega/resource.language.it_it
KODI21_RESOURCE_LANGUAGE_IT_IT_PLUGINNAME=resource.language.it_it

KODI21_PLUGIN_TARGET_DIR=$(TARGET_DIR)/usr/share/kodi/addons

define KODI21_RESOURCE_LANGUAGE_IT_IT_EXTRACT_CMDS
	@unzip -q -o \
	$(DL_DIR)/$(KODI21_RESOURCE_LANGUAGE_IT_IT_DL_SUBDIR)/$(KODI21_RESOURCE_LANGUAGE_IT_IT_SOURCE) \
	    -d $(@D)
endef

define KODI21_RESOURCE_LANGUAGE_IT_IT_INSTALL_TARGET_CMDS
	@mkdir -p $(KODI21_PLUGIN_TARGET_DIR)
	@cp -r $(@D)/$(KODI21_RESOURCE_LANGUAGE_IT_IT_PLUGINNAME) \
	    $(KODI21_PLUGIN_TARGET_DIR)
endef

$(eval $(generic-package))
