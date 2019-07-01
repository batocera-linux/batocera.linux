################################################################################
#
# Batocera desktop applications
#
################################################################################
BATOCERA_DESKTOPAPPS_VERSION = 1.0
BATOCERA_DESKTOPAPPS_SOURCE=  

BATOCERA_DESKTOPAPPS_SCRIPTS = filemanagerlauncher.sh
BATOCERA_DESKTOPAPPS_APPS  = xterm.desktop
BATOCERA_DESKTOPAPPS_ICONS =

# pcsx2
ifneq ($(BR2_PACKAGE_PCSX2_X86)$(BR2_PACKAGE_PCSX2)$(BR2_PACKAGE_PCSX2_AVX2),)
  BATOCERA_DESKTOPAPPS_SCRIPTS += batocera-config-pcsx2.sh
  BATOCERA_DESKTOPAPPS_APPS    += pcsx2-config.desktop
	BATOCERA_DESKTOPAPPS_ICONS   += pcsx2.png
endif

# dolphin
ifeq ($(BR2_PACKAGE_DOLPHIN_EMU),y)
  BATOCERA_DESKTOPAPPS_SCRIPTS += batocera-config-dolphin.sh
  BATOCERA_DESKTOPAPPS_APPS    += dolphin-config.desktop
	BATOCERA_DESKTOPAPPS_ICONS   += dolphin.png
endif

# retroarch
ifeq ($(BR2_PACKAGE_RETROARCH),y)
  BATOCERA_DESKTOPAPPS_SCRIPTS += batocera-config-retroarch.sh
  BATOCERA_DESKTOPAPPS_APPS    += retroarch-config.desktop
	BATOCERA_DESKTOPAPPS_ICONS   += retroarch.png
endif

# ppsspp
ifeq ($(BR2_PACKAGE_PPSSPP),y)
  BATOCERA_DESKTOPAPPS_SCRIPTS += batocera-config-ppsspp.sh
  BATOCERA_DESKTOPAPPS_APPS    += ppsspp-config.desktop
	BATOCERA_DESKTOPAPPS_ICONS   += ppsspp.png
endif

# reicast
ifeq ($(BR2_PACKAGE_REICAST),y)
  BATOCERA_DESKTOPAPPS_SCRIPTS += batocera-config-reicast.sh
  BATOCERA_DESKTOPAPPS_APPS    += reicast-config.desktop
	BATOCERA_DESKTOPAPPS_ICONS   += reicast.png
endif

# scummvm
ifeq ($(BR2_PACKAGE_SCUMMVM),y)
  BATOCERA_DESKTOPAPPS_SCRIPTS += batocera-config-scummvm.sh
  BATOCERA_DESKTOPAPPS_APPS    += scummvm-config.desktop
	BATOCERA_DESKTOPAPPS_ICONS   += scummvm.png
endif

define BATOCERA_DESKTOPAPPS_INSTALL_TARGET_CMDS
	# scripts
	mkdir -p $(TARGET_DIR)/recalbox/scripts
	$(foreach f,$(BATOCERA_DESKTOPAPPS_SCRIPTS), cp package/batocera/core/batocera-desktopapps/scripts/$(f) $(TARGET_DIR)/recalbox/scripts/$(f)$(sep))

	# apps
	mkdir -p $(TARGET_DIR)/usr/share/applications
	$(foreach f,$(BATOCERA_DESKTOPAPPS_APPS), cp package/batocera/core/batocera-desktopapps/apps/$(f) $(TARGET_DIR)/usr/share/applications/$(f)$(sep))

	# icons
	mkdir -p $(TARGET_DIR)/usr/share/icons/batocera
	$(foreach f,$(BATOCERA_DESKTOPAPPS_ICONS), cp package/batocera/core/batocera-desktopapps/icons/$(f) $(TARGET_DIR)/usr/share/icons/batocera/$(f)$(sep))

	# menu
	mkdir -p $(TARGET_DIR)/etc/xdg/menus
	cp package/batocera/core/batocera-desktopapps/menu/batocera-applications.menu $(TARGET_DIR)/etc/xdg/menus/batocera-applications.menu
endef

$(eval $(generic-package))
