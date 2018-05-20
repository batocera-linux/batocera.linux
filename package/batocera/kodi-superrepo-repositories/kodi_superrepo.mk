################################################################################
#
# kodi supperrepo repositories
#
################################################################################

KODI_SUPERREPO_REPOSITORIES_VERSION = 0.7.04
KODI_SUPERREPO_REPOSITORIES_SOURCE = superrepo.kodi.krypton.repositories-$(KODI_SUPERREPO_REPOSITORIES_VERSION).zip
KODI_SUPERREPO_REPOSITORIES_SITE = http://srp.nu/krypton/repositories/superrepo
KODI_SUPERREPO_REPOSITORIES_PLUGINNAME=superrepo.kodi.krypton.repositories

KODI_PLUGIN_TARGET_DIR=$(TARGET_DIR)/usr/share/kodi/addons

define KODI_SUPERREPO_REPOSITORIES_EXTRACT_CMDS
	@unzip -q -o $(DL_DIR)/$(KODI_SUPERREPO_REPOSITORIES_DL_SUBDIR)/$(KODI_SUPERREPO_REPOSITORIES_SOURCE) -d $(@D)
endef

define KODI_SUPERREPO_REPOSITORIES_INSTALL_TARGET_CMDS
	@mkdir -p $(KODI_PLUGIN_TARGET_DIR)
	@cp -r $(@D)/$(KODI_SUPERREPO_REPOSITORIES_PLUGINNAME) $(KODI_PLUGIN_TARGET_DIR)
endef

$(eval $(generic-package))
