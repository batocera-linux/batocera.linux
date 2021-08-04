################################################################################
#
# batocera scripts
#
################################################################################

BATOCERA_SCRIPTS_VERSION = 3
BATOCERA_SCRIPTS_LICENSE = GPL
BATOCERA_SCRIPTS_DEPENDENCIES = pciutils
BATOCERA_SCRIPTS_SOURCE=

BATOCERA_SCRIPT_RESOLUTION_TYPE=basic
BATOCERA_SCRIPT_SCREENSHOT_TYPE=basic
ifeq ($(BR2_PACKAGE_RPI_USERLAND),y)
  BATOCERA_SCRIPT_RESOLUTION_TYPE=tvservice
  BATOCERA_SCRIPT_SCREENSHOT_TYPE=tvservice
endif
ifeq ($(BR2_PACKAGE_LIBDRM),y)
  BATOCERA_SCRIPT_RESOLUTION_TYPE=drm
  BATOCERA_SCRIPT_SCREENSHOT_TYPE=drm
endif
ifeq ($(BR2_PACKAGE_XORG7),y)
  BATOCERA_SCRIPT_RESOLUTION_TYPE=xorg
  BATOCERA_SCRIPT_SCREENSHOT_TYPE=xorg
endif

# doesn't work on odroidgoa with mali g31_gbm
ifeq ($(BR2_PACKAGE_MALI_G31_GBM),y)
  BATOCERA_SCRIPT_RESOLUTION_TYPE=basic
endif

define BATOCERA_SCRIPTS_INSTALL_TARGET_CMDS
	install -m 0755 $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/core/batocera-scripts/scripts/bluetooth/bluezutils.py            $(TARGET_DIR)/usr/lib/python3.9/ # any variable ?
	install -m 0755 $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/core/batocera-scripts/scripts/bluetooth/batocera-bluetooth       $(TARGET_DIR)/usr/bin/
	install -m 0755 $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/core/batocera-scripts/scripts/bluetooth/batocera-bluetooth-agent $(TARGET_DIR)/usr/bin/
	install -m 0755 $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/core/batocera-scripts/scripts/batocera-save-overlay           $(TARGET_DIR)/usr/bin/
	install -m 0755 $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/core/batocera-scripts/scripts/batocera-es-theme               $(TARGET_DIR)/usr/bin/
	install -m 0755 $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/core/batocera-scripts/scripts/batocera-kodi                   $(TARGET_DIR)/usr/bin/
	install -m 0755 $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/core/batocera-scripts/scripts/batocera-kodilauncher           $(TARGET_DIR)/usr/bin/
	install -m 0755 $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/core/batocera-scripts/scripts/batocera-usbmount               $(TARGET_DIR)/usr/bin/
	install -m 0755 $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/core/batocera-scripts/scripts/batocera-encode                 $(TARGET_DIR)/usr/bin/
	install -m 0755 $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/core/batocera-scripts/scripts/batocera-padsinfo               $(TARGET_DIR)/usr/bin/
	install -m 0755 $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/core/batocera-scripts/scripts/batocera-info                   $(TARGET_DIR)/usr/bin/
	install -m 0755 $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/core/batocera-scripts/scripts/batocera-install                $(TARGET_DIR)/usr/bin/
	install -m 0755 $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/core/batocera-scripts/scripts/batocera-format                 $(TARGET_DIR)/usr/bin/
	install -m 0755 $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/core/batocera-scripts/scripts/batocera-mount                  $(TARGET_DIR)/usr/bin/
	install -m 0755 $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/core/batocera-scripts/scripts/batocera-overclock              $(TARGET_DIR)/usr/bin/
	install -m 0755 $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/core/batocera-scripts/scripts/batocera-part                   $(TARGET_DIR)/usr/bin/
	install -m 0755 $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/core/batocera-scripts/scripts/batocera-support                $(TARGET_DIR)/usr/bin/
	install -m 0755 $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/core/batocera-scripts/scripts/batocera-sync                   $(TARGET_DIR)/usr/bin/
	install -m 0755 $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/core/batocera-scripts/scripts/batocera-upgrade                $(TARGET_DIR)/usr/bin/
	install -m 0755 $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/core/batocera-scripts/scripts/batocera-systems                $(TARGET_DIR)/usr/bin/
	install -m 0755 $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/core/batocera-scripts/scripts/batocera-config                 $(TARGET_DIR)/usr/bin/
	install -m 0755 $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/core/batocera-scripts/scripts/batocera-es-thebezelproject     $(TARGET_DIR)/usr/bin/
	install -m 0755 $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/core/batocera-scripts/scripts/batocera-cores                  $(TARGET_DIR)/usr/bin/
	install -m 0755 $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/core/batocera-scripts/scripts/batocera-hybrid-nvidia          $(TARGET_DIR)/usr/bin/
	install -m 0755 $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/core/batocera-scripts/scripts/batocera-wifi                   $(TARGET_DIR)/usr/bin/
	install -m 0755 $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/core/batocera-scripts/scripts/batocera-brightness             $(TARGET_DIR)/usr/bin/
	install -m 0755 $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/core/batocera-scripts/scripts/batocera-es-swissknife          $(TARGET_DIR)/usr/bin/
	install -m 0755 $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/core/batocera-scripts/scripts/batocera-create-collection      $(TARGET_DIR)/usr/bin/
	install -m 0755 $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/core/batocera-scripts/scripts/batocera-store                  $(TARGET_DIR)/usr/bin/
	install -m 0755 $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/core/batocera-scripts/scripts/batocera-autologin              $(TARGET_DIR)/usr/bin/
	install -m 0755 $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/core/batocera-scripts/scripts/batocera-resolution.$(BATOCERA_SCRIPT_RESOLUTION_TYPE) $(TARGET_DIR)/usr/bin/batocera-resolution
	install -m 0755 $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/core/batocera-scripts/scripts/batocera-screenshot.$(BATOCERA_SCRIPT_SCREENSHOT_TYPE) $(TARGET_DIR)/usr/bin/batocera-screenshot
	install -m 0755 $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/core/batocera-scripts/scripts/batocera-timezone               $(TARGET_DIR)/usr/bin/
    install -m 0755 $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/core/batocera-scripts/scripts/batocera-gameforce              $(TARGET_DIR)/usr/bin/
endef

define BATOCERA_SCRIPTS_INSTALL_XORG
	mkdir -p $(TARGET_DIR)/etc/X11/xorg.conf.d
	cp -prn $(BR2_EXTERNAL_BATOCERA_PATH)/board/batocera/x86/fsoverlay/etc/X11/xorg.conf.d/20-amdgpu.conf $(TARGET_DIR)/etc/X11/xorg.conf.d/20-amdgpu.conf
	ln -fs /userdata/system/99-nvidia.conf $(TARGET_DIR)/etc/X11/xorg.conf.d/99-nvidia.conf
	install -m 0755 $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/core/batocera-scripts/scripts/batocera-record $(TARGET_DIR)/usr/bin/
endef

define BATOCERA_SCRIPTS_INSTALL_ROCKCHIP
	install -m 0755 $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/core/batocera-scripts/scripts/batocera-rockchip-suspend $(TARGET_DIR)/usr/bin/
endef

ifeq ($(BR2_PACKAGE_XSERVER_XORG_SERVER),y)
  BATOCERA_SCRIPTS_POST_INSTALL_TARGET_HOOKS += BATOCERA_SCRIPTS_INSTALL_XORG
endif

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_ROCKCHIP_ANY),y)
  BATOCERA_SCRIPTS_POST_INSTALL_TARGET_HOOKS += BATOCERA_SCRIPTS_INSTALL_ROCKCHIP
endif

$(eval $(generic-package))
