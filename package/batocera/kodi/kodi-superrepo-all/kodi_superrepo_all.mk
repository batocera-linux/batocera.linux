################################################################################
#
# kodi supperrepo all
#
################################################################################

KODI_SUPERREPO_ALL_VERSION = 0.7.04
KODI_SUPERREPO_ALL_SOURCE = superrepo.kodi.krypton.all-$(KODI_SUPERREPO_ALL_VERSION).zip
KODI_SUPERREPO_ALL_SITE = http://redirect.superrepo.org/v7/addons/superrepo.kodi.krypton.all
KODI_SUPERREPO_ALL_PLUGINNAME=superrepo.kodi.krypton.all

KODI_PLUGIN_TARGET_DIR=$(TARGET_DIR)/usr/share/kodi/addons

define KODI_SUPERREPO_ALL_EXTRACT_CMDS
	@unzip -q -o $(DL_DIR)/$(KODI_SUPERREPO_ALL_DL_SUBDIR)/$(KODI_SUPERREPO_ALL_SOURCE) -d $(@D)
endef

define KODI_SUPERREPO_ALL_INSTALL_TARGET_CMDS
	@mkdir -p $(KODI_PLUGIN_TARGET_DIR)
	@cp -r $(@D)/$(KODI_SUPERREPO_ALL_PLUGINNAME) $(KODI_PLUGIN_TARGET_DIR)
endef

$(eval $(generic-package))
