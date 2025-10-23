################################################################################
#
# kodi21 tr_tr language resource
#
################################################################################

KODI21_RESOURCE_LANGUAGE_TR_TR_VERSION = 11.0.85
KODI21_RESOURCE_LANGUAGE_TR_TR_SOURCE = \
    resource.language.tr_tr-$(KODI21_RESOURCE_LANGUAGE_TR_TR_VERSION).zip
KODI21_RESOURCE_LANGUAGE_TR_TR_SITE = \
    https://mirrors.kodi.tv/addons/omega/resource.language.tr_tr
KODI21_RESOURCE_LANGUAGE_TR_TR_PLUGINNAME=resource.language.tr_tr

KODI21_PLUGIN_TARGET_DIR=$(TARGET_DIR)/usr/share/kodi/addons

define KODI21_RESOURCE_LANGUAGE_TR_TR_EXTRACT_CMDS
	@unzip -q -o \
	$(DL_DIR)/$(KODI21_RESOURCE_LANGUAGE_TR_TR_DL_SUBDIR)/$(KODI21_RESOURCE_LANGUAGE_TR_TR_SOURCE) \
	    -d $(@D)
endef

define KODI21_RESOURCE_LANGUAGE_TR_TR_INSTALL_TARGET_CMDS
	@mkdir -p $(KODI21_PLUGIN_TARGET_DIR)
	@cp -r $(@D)/$(KODI21_RESOURCE_LANGUAGE_TR_TR_PLUGINNAME) \
	    $(KODI21_PLUGIN_TARGET_DIR)
endef

$(eval $(generic-package))
