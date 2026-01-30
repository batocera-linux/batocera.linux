################################################################################
#
# batocera-desktopapps
#
################################################################################

BATOCERA_DESKTOPAPPS_VERSION = 1.1
BATOCERA_DESKTOPAPPS_SOURCE =

BATOCERA_DESKTOPAPPS_PKGDIR = \
    $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/core/batocera-desktopapps

# Base files
BATOCERA_DESKTOPAPPS_SCRIPTS = filemanagerlauncher
BATOCERA_DESKTOPAPPS_APPS    = xterm.desktop
BATOCERA_DESKTOPAPPS_ICONS   =
BATOCERA_DESKTOPAPPS_TOOLBOX =
BATOCERA_DESKTOPAPPS_ACTIONS = system.md5sum.desktop

#file-roller integration for pcmanfm - open/list archives
BATOCERA_DESKTOPAPPS_APPS    += file-roller-mimics.desktop

## System depended applets

# wiimote
BATOCERA_DESKTOPAPPS_APPS    += xwiishowir.desktop
BATOCERA_DESKTOPAPPS_ICONS   += xwiishowir.png

# pcsx2
ifeq ($(BR2_PACKAGE_PCSX2),y)
  BATOCERA_DESKTOPAPPS_SCRIPTS += batocera-config-pcsx2
  BATOCERA_DESKTOPAPPS_APPS    += pcsx2-config.desktop
  BATOCERA_DESKTOPAPPS_ICONS   += pcsx2.png
endif

# dolphin
ifeq ($(BR2_PACKAGE_DOLPHIN_EMU)$(BR2_PACKAGE_XORG7),yy)
  BATOCERA_DESKTOPAPPS_SCRIPTS += batocera-config-dolphin
  BATOCERA_DESKTOPAPPS_APPS    += dolphin-config.desktop
  BATOCERA_DESKTOPAPPS_ICONS   += dolphin.png
endif

# dolphin-triforce
ifeq ($(BR2_PACKAGE_DOLPHIN_TRIFORCE),y)
  BATOCERA_DESKTOPAPPS_SCRIPTS += batocera-config-dolphin-triforce
  BATOCERA_DESKTOPAPPS_APPS    += dolphin-triforce-config.desktop
  BATOCERA_DESKTOPAPPS_ICONS   += dolphin-triforce.png
endif

# duckstation
ifeq ($(BR2_PACKAGE_DUCKSTATION),y)
  BATOCERA_DESKTOPAPPS_SCRIPTS += batocera-config-duckstation
  BATOCERA_DESKTOPAPPS_APPS    += duckstation-config.desktop
  BATOCERA_DESKTOPAPPS_ICONS   += duckstation.png
endif

# retroarch
ifeq ($(BR2_PACKAGE_RETROARCH),y)
  BATOCERA_DESKTOPAPPS_SCRIPTS += batocera-config-retroarch
  BATOCERA_DESKTOPAPPS_APPS    += retroarch-config.desktop
  BATOCERA_DESKTOPAPPS_ICONS   += retroarch.png
endif

# ppsspp
ifeq ($(BR2_PACKAGE_PPSSPP),y)
  BATOCERA_DESKTOPAPPS_SCRIPTS += batocera-config-ppsspp
  BATOCERA_DESKTOPAPPS_APPS    += ppsspp-config.desktop
  BATOCERA_DESKTOPAPPS_ICONS   += ppsspp.png
endif

# flycast
ifeq ($(BR2_PACKAGE_FLYCAST),y)
  BATOCERA_DESKTOPAPPS_SCRIPTS += batocera-config-flycast
  BATOCERA_DESKTOPAPPS_APPS    += flycast-config.desktop
  BATOCERA_DESKTOPAPPS_ICONS   += flycast.png
endif

# scummvm
ifeq ($(BR2_PACKAGE_SCUMMVM),y)
  BATOCERA_DESKTOPAPPS_SCRIPTS += batocera-config-scummvm
  BATOCERA_DESKTOPAPPS_APPS    += scummvm-config.desktop
  BATOCERA_DESKTOPAPPS_ICONS   += scummvm.png
endif

# azahar
ifeq ($(BR2_PACKAGE_AZAHAR),y)
  BATOCERA_DESKTOPAPPS_SCRIPTS += batocera-config-azahar
  BATOCERA_DESKTOPAPPS_APPS    += azahar-config.desktop
  BATOCERA_DESKTOPAPPS_ICONS   += azahar.png
endif

# rpcs3
ifeq ($(BR2_PACKAGE_RPCS3),y)
  BATOCERA_DESKTOPAPPS_SCRIPTS += batocera-config-rpcs3
  BATOCERA_DESKTOPAPPS_APPS    += rpcs3-config.desktop
  BATOCERA_DESKTOPAPPS_ICONS   += rpcs3.png
endif

# cemu
ifeq ($(BR2_PACKAGE_CEMU),y)
  BATOCERA_DESKTOPAPPS_SCRIPTS += batocera-config-cemu
  BATOCERA_DESKTOPAPPS_APPS    += cemu-config.desktop
  BATOCERA_DESKTOPAPPS_ICONS   += cemu.png
endif

# model2emu
ifeq ($(BR2_PACKAGE_MODEL2EMU),y)
  BATOCERA_DESKTOPAPPS_SCRIPTS += batocera-config-model2emu
  BATOCERA_DESKTOPAPPS_APPS    += model2emu-config.desktop
  BATOCERA_DESKTOPAPPS_ICONS   += model2emu.png
endif

# flatpak
ifeq ($(BR2_PACKAGE_BAUH),y)
  BATOCERA_DESKTOPAPPS_APPS    += flatpak-config.desktop
endif

# citron
ifeq ($(BR2_PACKAGE_CITRON),y)
  BATOCERA_DESKTOPAPPS_SCRIPTS += batocera-config-citron
  BATOCERA_DESKTOPAPPS_APPS    += citron-config.desktop
  BATOCERA_DESKTOPAPPS_ICONS   += citron.png
endif

# ryujinx
ifeq ($(BR2_PACKAGE_RYUJINX),y)
  BATOCERA_DESKTOPAPPS_SCRIPTS += batocera-config-ryujinx
  BATOCERA_DESKTOPAPPS_APPS    += ryujinx-config.desktop
  BATOCERA_DESKTOPAPPS_ICONS   += ryujinx.png
endif

# melonds
ifeq ($(BR2_PACKAGE_DEMUL),y)
  BATOCERA_DESKTOPAPPS_SCRIPTS += batocera-config-melonds
  BATOCERA_DESKTOPAPPS_APPS    += melonds-config.desktop
  BATOCERA_DESKTOPAPPS_ICONS   += melonds.png
endif

# xenia
ifeq ($(BR2_PACKAGE_XENIA),y)
  BATOCERA_DESKTOPAPPS_SCRIPTS += batocera-config-xenia
  BATOCERA_DESKTOPAPPS_APPS    += xenia-config.desktop
  BATOCERA_DESKTOPAPPS_ICONS   += xenia.png
endif

# xenia-canary
ifeq ($(BR2_PACKAGE_XENIA_CANARY),y)
  BATOCERA_DESKTOPAPPS_SCRIPTS += batocera-config-xenia-canary
  BATOCERA_DESKTOPAPPS_APPS    += xenia-canary-config.desktop
  BATOCERA_DESKTOPAPPS_ICONS   += xenia-canary.png
endif

# vita3k
ifeq ($(BR2_PACKAGE_VITA3K),y)
  BATOCERA_DESKTOPAPPS_SCRIPTS += batocera-config-vita3k
  BATOCERA_DESKTOPAPPS_APPS    += vita3k-config.desktop
  BATOCERA_DESKTOPAPPS_ICONS   += vita3k.png
endif

# play!
ifeq ($(BR2_PACKAGE_PLAY),y)
  BATOCERA_DESKTOPAPPS_SCRIPTS += batocera-config-play
  BATOCERA_DESKTOPAPPS_APPS    += play-config.desktop
  BATOCERA_DESKTOPAPPS_ICONS   += play.png
endif

# shadPS4
ifeq ($(BR2_PACKAGE_SHADPS4),y)
  BATOCERA_DESKTOPAPPS_SCRIPTS += batocera-config-shadps4
  BATOCERA_DESKTOPAPPS_APPS    += shadps4-config.desktop
  BATOCERA_DESKTOPAPPS_ICONS   += shadps4.png
endif

# lindbergh loader
ifeq ($(BR2_PACKAGE_LINDBERGH_LOADER),y)
  BATOCERA_DESKTOPAPPS_SCRIPTS += batocera-config-lindbergh
endif

## Context Menu Actions

# m3u playlists for psx, segacd, systems that support m3u
BATOCERA_DESKTOPAPPS_TOOLBOX += multidisc.toolbox
BATOCERA_DESKTOPAPPS_ACTIONS += multidisc.toolbox.m3ufromdir.desktop

# wine
ifeq ($(BR2_PACKAGE_WINE_TKG),y)
  BATOCERA_DESKTOPAPPS_TOOLBOX += wine.toolbox
  BATOCERA_DESKTOPAPPS_ACTIONS += wine.toolbox.configit.desktop
  BATOCERA_DESKTOPAPPS_ACTIONS += wine.toolbox.wsquashfs.desktop
  BATOCERA_DESKTOPAPPS_ACTIONS += wine.toolbox.symlinkprefix.desktop
  BATOCERA_DESKTOPAPPS_ACTIONS += wine.toolbox.listprefix.desktop
  BATOCERA_DESKTOPAPPS_ACTIONS += wine.toolbox.folder2autorun.desktop
  BATOCERA_DESKTOPAPPS_ACTIONS += wine.toolbox.file2autorun.desktop
  BATOCERA_DESKTOPAPPS_ACTIONS += wine.toolbox.extract.desktop
endif

# dosbox
ifeq ($(BR2_PACKAGE_DOSBOX),y)
  BATOCERA_DESKTOPAPPS_TOOLBOX += dos.toolbox
  BATOCERA_DESKTOPAPPS_ACTIONS += dos.toolbox.configit.desktop
  BATOCERA_DESKTOPAPPS_ACTIONS += dos.toolbox.squashfs.desktop
  BATOCERA_DESKTOPAPPS_ACTIONS += dos.toolbox.folder2autorun.desktop
  BATOCERA_DESKTOPAPPS_ACTIONS += dos.toolbox.file2autorun.desktop
  BATOCERA_DESKTOPAPPS_ACTIONS += dos.toolbox.extract.desktop
endif


define BATOCERA_DESKTOPAPPS_INSTALL_TARGET_CMDS
	# scripts (Install as executable 0755)
	$(foreach f,$(BATOCERA_DESKTOPAPPS_SCRIPTS),\
		$(INSTALL) -D -m 0755 $(BATOCERA_DESKTOPAPPS_PKGDIR)/scripts/$(f) \
			$(TARGET_DIR)/usr/bin/$(f)$(sep))

	# apps (Install as data 0644)
	$(foreach f,$(BATOCERA_DESKTOPAPPS_APPS),\
		$(INSTALL) -D -m 0644 $(BATOCERA_DESKTOPAPPS_PKGDIR)/apps/$(f) \
			$(TARGET_DIR)/usr/share/applications/$(f)$(sep))

	# default-mime types
	$(INSTALL) -D -m 0644 $(BATOCERA_DESKTOPAPPS_PKGDIR)/mime/defaults.list \
		$(TARGET_DIR)/usr/share/applications/defaults.list

	# icons
	$(foreach f,$(BATOCERA_DESKTOPAPPS_ICONS),\
		$(INSTALL) -D -m 0644 $(BATOCERA_DESKTOPAPPS_PKGDIR)/icons/$(f) \
			$(TARGET_DIR)/usr/share/icons/batocera/$(f)$(sep))

	# context menu actions
	$(foreach f,$(BATOCERA_DESKTOPAPPS_ACTIONS),\
		$(INSTALL) -D -m 0644 $(BATOCERA_DESKTOPAPPS_PKGDIR)/contextactions/$(f) \
			$(TARGET_DIR)/usr/share/file-manager/actions/$(f)$(sep))

	# toolbox (Install as executable 0755)
	$(foreach f,$(BATOCERA_DESKTOPAPPS_TOOLBOX),\
		$(INSTALL) -D -m 0755 $(BATOCERA_DESKTOPAPPS_PKGDIR)/toolbox/$(f) \
			$(TARGET_DIR)/usr/share/file-manager/actions/toolbox/$(f)$(sep))

	# menu
	$(INSTALL) -D -m 0644 $(BATOCERA_DESKTOPAPPS_PKGDIR)/menu/batocera-applications.menu \
		$(TARGET_DIR)/etc/xdg/menus/batocera-applications.menu
endef

$(eval $(generic-package))
