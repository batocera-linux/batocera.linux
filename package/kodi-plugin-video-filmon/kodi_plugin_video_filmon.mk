################################################################################
#
# kodi filmon plugin
#
################################################################################

KODI_PLUGIN_VIDEO_FILMON_VERSION = 4.6.7
KODI_PLUGIN_VIDEO_FILMON_SOURCE = plugin.video.filmon-$(KODI_PLUGIN_VIDEO_FILMON_VERSION).zip
KODI_PLUGIN_VIDEO_FILMON_SITE = http://redirect.superrepo.org/v7/addons/plugin.video.filmon
KODI_PLUGIN_VIDEO_FILMON_PLUGINNAME=plugin.video.filmon

KODI_PLUGIN_TARGET_DIR=$(TARGET_DIR)/usr/share/kodi/addons

define KODI_PLUGIN_VIDEO_FILMON_EXTRACT_CMDS
	@unzip -q -o $(DL_DIR)/$(KODI_PLUGIN_VIDEO_FILMON_SOURCE) -d $(@D)
endef

define KODI_PLUGIN_VIDEO_FILMON_INSTALL_TARGET_CMDS
	@mkdir -p $(KODI_PLUGIN_TARGET_DIR)
	@cp -r $(@D)/$(KODI_PLUGIN_VIDEO_FILMON_PLUGINNAME) $(KODI_PLUGIN_TARGET_DIR)
endef

$(eval $(generic-package))
