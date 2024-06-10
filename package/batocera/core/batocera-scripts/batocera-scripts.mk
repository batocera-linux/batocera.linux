################################################################################
#
# batocera scripts
#
################################################################################

BATOCERA_SCRIPTS_VERSION = 3
BATOCERA_SCRIPTS_LICENSE = GPL
BATOCERA_SCRIPTS_DEPENDENCIES = pciutils
BATOCERA_SCRIPTS_SOURCE=

BATOCERA_SCRIPTS_PATH = $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/core/batocera-scripts

# mouse type #
ifeq ($(BR2_PACKAGE_XSERVER_XORG_SERVER),y)
  BATOCERA_SCRIPTS_MOUSE_TYPE=xorg
  BATOCERA_SCRIPTS_POST_INSTALL_TARGET_HOOKS += BATOCERA_SCRIPTS_INSTALL_MOUSE
endif

ifeq ($(BR2_PACKAGE_BATOCERA_WAYLAND_SWAY),y)
  BATOCERA_SCRIPTS_MOUSE_TYPE=wayland-sway
  BATOCERA_SCRIPTS_POST_INSTALL_TARGET_HOOKS += BATOCERA_SCRIPTS_INSTALL_MOUSE
endif
###

define BATOCERA_SCRIPTS_INSTALL_TARGET_CMDS
    mkdir -p $(TARGET_DIR)/usr/lib/python$(PYTHON3_VERSION_MAJOR)
    mkdir -p $(TARGET_DIR)/usr/bin
    install -m 0755 $(BATOCERA_SCRIPTS_PATH)/scripts/bluetooth/bluezutils.py            $(TARGET_DIR)/usr/lib/python$(PYTHON3_VERSION_MAJOR)/ # any variable ?
    install -m 0755 $(BATOCERA_SCRIPTS_PATH)/scripts/bluetooth/batocera-bluetooth       $(TARGET_DIR)/usr/bin/
    install -m 0755 $(BATOCERA_SCRIPTS_PATH)/scripts/bluetooth/batocera-bluetooth-agent $(TARGET_DIR)/usr/bin/
    install -m 0755 $(BATOCERA_SCRIPTS_PATH)/scripts/batocera-save-overlay              $(TARGET_DIR)/usr/bin/
    install -m 0755 $(BATOCERA_SCRIPTS_PATH)/scripts/batocera-kodi                      $(TARGET_DIR)/usr/bin/
    install -m 0755 $(BATOCERA_SCRIPTS_PATH)/scripts/batocera-kodilauncher              $(TARGET_DIR)/usr/bin/
    install -m 0755 $(BATOCERA_SCRIPTS_PATH)/scripts/batocera-usbmount                  $(TARGET_DIR)/usr/bin/
    install -m 0755 $(BATOCERA_SCRIPTS_PATH)/scripts/batocera-encode                    $(TARGET_DIR)/usr/bin/
    install -m 0755 $(BATOCERA_SCRIPTS_PATH)/scripts/batocera-padsinfo                  $(TARGET_DIR)/usr/bin/
    install -m 0755 $(BATOCERA_SCRIPTS_PATH)/scripts/batocera-info                      $(TARGET_DIR)/usr/bin/
    install -m 0755 $(BATOCERA_SCRIPTS_PATH)/scripts/batocera-install                   $(TARGET_DIR)/usr/bin/
    install -m 0755 $(BATOCERA_SCRIPTS_PATH)/scripts/batocera-format                    $(TARGET_DIR)/usr/bin/
    install -m 0755 $(BATOCERA_SCRIPTS_PATH)/scripts/batocera-mount                     $(TARGET_DIR)/usr/bin/
    install -m 0755 $(BATOCERA_SCRIPTS_PATH)/scripts/batocera-overclock                 $(TARGET_DIR)/usr/bin/
    install -m 0755 $(BATOCERA_SCRIPTS_PATH)/scripts/batocera-part                      $(TARGET_DIR)/usr/bin/
    install -m 0755 $(BATOCERA_SCRIPTS_PATH)/scripts/batocera-support                   $(TARGET_DIR)/usr/bin/
    install -m 0755 $(BATOCERA_SCRIPTS_PATH)/scripts/batocera-version                   $(TARGET_DIR)/usr/bin/
    install -m 0755 $(BATOCERA_SCRIPTS_PATH)/scripts/batocera-sync                      $(TARGET_DIR)/usr/bin/
    install -m 0755 $(BATOCERA_SCRIPTS_PATH)/scripts/batocera-upgrade                   $(TARGET_DIR)/usr/bin/
    install -m 0755 $(BATOCERA_SCRIPTS_PATH)/scripts/batocera-systems                   $(TARGET_DIR)/usr/bin/
    install -m 0755 $(BATOCERA_SCRIPTS_PATH)/scripts/batocera-config                    $(TARGET_DIR)/usr/bin/
    install -m 0755 $(BATOCERA_SCRIPTS_PATH)/scripts/batocera-es-thebezelproject        $(TARGET_DIR)/usr/bin/
    install -m 0755 $(BATOCERA_SCRIPTS_PATH)/scripts/batocera-cores                     $(TARGET_DIR)/usr/bin/
    install -m 0755 $(BATOCERA_SCRIPTS_PATH)/scripts/batocera-wifi                      $(TARGET_DIR)/usr/bin/
    install -m 0755 $(BATOCERA_SCRIPTS_PATH)/scripts/batocera-brightness                $(TARGET_DIR)/usr/bin/
    install -m 0755 $(BATOCERA_SCRIPTS_PATH)/scripts/batocera-es-swissknife             $(TARGET_DIR)/usr/bin/
    install -m 0755 $(BATOCERA_SCRIPTS_PATH)/scripts/batocera-store                     $(TARGET_DIR)/usr/bin/
    install -m 0755 $(BATOCERA_SCRIPTS_PATH)/scripts/batocera-autologin                 $(TARGET_DIR)/usr/bin/
    install -m 0755 $(BATOCERA_SCRIPTS_PATH)/scripts/batocera-timezone                  $(TARGET_DIR)/usr/bin/
    install -m 0755 $(BATOCERA_SCRIPTS_PATH)/scripts/batocera-gameforce                 $(TARGET_DIR)/usr/bin/
    install -m 0755 $(BATOCERA_SCRIPTS_PATH)/scripts/batocera-shutdown                  $(TARGET_DIR)/usr/bin/
    install -m 0755 $(BATOCERA_SCRIPTS_PATH)/scripts/batocera-services                  $(TARGET_DIR)/usr/bin/
    install -m 0755 $(BATOCERA_SCRIPTS_PATH)/scripts/batocera-planemode                 $(TARGET_DIR)/usr/bin/
    install -m 0755 $(BATOCERA_SCRIPTS_PATH)/scripts/batocera-switch-screen-checker     $(TARGET_DIR)/usr/bin/
    install -m 0755 $(BATOCERA_SCRIPTS_PATH)/scripts/batocera-switch-screen-checker-delayed     $(TARGET_DIR)/usr/bin/
    install -m 0755 $(BATOCERA_SCRIPTS_PATH)/scripts/batocera-ikemen                    $(TARGET_DIR)/usr/bin/
    install -m 0755 $(BATOCERA_SCRIPTS_PATH)/scripts/batocera-streaming                 $(TARGET_DIR)/usr/bin/
    install -m 0644 $(BATOCERA_SCRIPTS_PATH)/rules/80-switch-screen.rules               $(TARGET_DIR)/etc/udev/rules.d
    mkdir -p $(TARGET_DIR)/etc/udev/rules.d
    install -m 0755 $(BATOCERA_SCRIPTS_PATH)/scripts/batocera-amd-tdp                   $(TARGET_DIR)/usr/bin/
    install -m 0755 $(BATOCERA_SCRIPTS_PATH)/scripts/batocera-get-nvidia-list           $(TARGET_DIR)/usr/bin/
    install -m 0755 $(BATOCERA_SCRIPTS_PATH)/scripts/batocera-led-effects               $(TARGET_DIR)/usr/bin/
    install -m 0755 $(BATOCERA_SCRIPTS_PATH)/scripts/batocera-spinner-calibrator        $(TARGET_DIR)/usr/bin/
    install -m 0755 $(BATOCERA_SCRIPTS_PATH)/scripts/batocera-vulkan                    $(TARGET_DIR)/usr/bin/
    install -m 0755 $(BATOCERA_SCRIPTS_PATH)/scripts/batocera-power-mode                $(TARGET_DIR)/usr/bin/
endef

define BATOCERA_SCRIPTS_INSTALL_MOUSE
    install -m 0755 $(BATOCERA_SCRIPTS_PATH)/scripts/batocera-mouse.${BATOCERA_SCRIPTS_MOUSE_TYPE} $(TARGET_DIR)/usr/bin/batocera-mouse
endef

define BATOCERA_SCRIPTS_INSTALL_ROCKCHIP
    mkdir -p $(TARGET_DIR)/usr/bin/
    install -m 0755 $(BATOCERA_SCRIPTS_PATH)/scripts/batocera-rockchip-suspend $(TARGET_DIR)/usr/bin/
endef

$(eval $(generic-package))
