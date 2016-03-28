################################################################################
#
# kodi filmon plugin
#
################################################################################

KODI_SCRIPT_MODULE_T0MM0_COMMON_VERSION = 2.1.1
KODI_SCRIPT_MODULE_T0MM0_COMMON_SOURCE = script.module.t0mm0.common-$(KODI_SCRIPT_MODULE_T0MM0_COMMON_VERSION).zip
KODI_SCRIPT_MODULE_T0MM0_COMMON_SITE = "http://mirrors.kodi.tv/addons/jarvis/script.module.t0mm0.common"
KODI_SCRIPT_MODULE_T0MM0_COMMON_PLUGINNAME=script.module.t0mm0.common

KODI_PLUGIN_TARGET_DIR=$(TARGET_DIR)/usr/share/kodi/addons

define KODI_SCRIPT_MODULE_T0MM0_COMMON_EXTRACT_CMDS
	@unzip -q -o $(DL_DIR)/$(KODI_SCRIPT_MODULE_T0MM0_COMMON_SOURCE) -d $(@D)
endef

define KODI_SCRIPT_MODULE_T0MM0_COMMON_INSTALL_TARGET_CMDS
	@mkdir -p $(KODI_PLUGIN_TARGET_DIR)
	@cp -r $(@D)/$(KODI_SCRIPT_MODULE_T0MM0_COMMON_PLUGINNAME) $(KODI_PLUGIN_TARGET_DIR)
endef

$(eval $(generic-package))
