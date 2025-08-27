################################################################################
#
# kodi21 pt_br language resource
#
################################################################################

KODI21_RESOURCE_LANGUAGE_PT_BR_VERSION = 11.0.95
KODI21_RESOURCE_LANGUAGE_PT_BR_SOURCE = \
    resource.language.pt_br-$(KODI21_RESOURCE_LANGUAGE_PT_BR_VERSION).zip
KODI21_RESOURCE_LANGUAGE_PT_BR_SITE = \
    https://mirrors.kodi.tv/addons/omega/resource.language.pt_br
KODI21_RESOURCE_LANGUAGE_PT_BR_PLUGINNAME=resource.language.pt_br

KODI21_PLUGIN_TARGET_DIR=$(TARGET_DIR)/usr/share/kodi/addons

define KODI21_RESOURCE_LANGUAGE_PT_BR_EXTRACT_CMDS
	@unzip -q -o \
	    $(DL_DIR)/$(KODI21_RESOURCE_LANGUAGE_PT_BR_DL_SUBDIR)/$(KODI21_RESOURCE_LANGUAGE_PT_BR_SOURCE) \
	    -d $(@D)
endef

define KODI21_RESOURCE_LANGUAGE_PT_BR_INSTALL_TARGET_CMDS
	@mkdir -p $(KODI21_PLUGIN_TARGET_DIR)
	@cp -r $(@D)/$(KODI21_RESOURCE_LANGUAGE_PT_BR_PLUGINNAME) \
	    $(KODI21_PLUGIN_TARGET_DIR)
endef

$(eval $(generic-package))
