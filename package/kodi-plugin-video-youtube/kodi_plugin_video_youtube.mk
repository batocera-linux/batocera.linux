################################################################################
#
# kodi youtube plugin
#
################################################################################

KODI_PLUGIN_VIDEO_YOUTUBE_VERSION = 5.3.6
KODI_PLUGIN_VIDEO_YOUTUBE_SOURCE = plugin.video.youtube-$(KODI_PLUGIN_VIDEO_YOUTUBE_VERSION).zip
KODI_PLUGIN_VIDEO_YOUTUBE_SITE = http://mirrors.kodi.tv/addons/jarvis/plugin.video.youtube
KODI_PLUGIN_VIDEO_YOUTUBE_PLUGINNAME=plugin.video.youtube

KODI_PLUGIN_TARGET_DIR=$(TARGET_DIR)/usr/share/kodi/addons

define KODI_PLUGIN_VIDEO_YOUTUBE_EXTRACT_CMDS
	@unzip -q -o $(DL_DIR)/$(KODI_PLUGIN_VIDEO_YOUTUBE_SOURCE) -d $(@D)
endef

define KODI_PLUGIN_VIDEO_YOUTUBE_INSTALL_TARGET_CMDS
	@mkdir -p $(KODI_PLUGIN_TARGET_DIR)
	@cp -r $(@D)/$(KODI_PLUGIN_VIDEO_YOUTUBE_PLUGINNAME) $(KODI_PLUGIN_TARGET_DIR)
endef

$(eval $(generic-package))
