################################################################################
#
# batocera.linux System
#
################################################################################

BATOCERA_SYSTEM_SOURCE=

BATOCERA_SYSTEM_VERSION = 44-dev
BATOCERA_SYSTEM_DATE_TIME = $(shell date "+%Y/%m/%d %H:%M")
BATOCERA_SYSTEM_DATE = $(shell date "+%Y/%m/%d")
BATOCERA_SYSTEM_DEPENDENCIES = tzdata
BATOCERA_SYSTEM_INSTALL_IMAGES = YES

BATOCERA_SYSTEM_VERSION_WITH_DATE = $(BATOCERA_SYSTEM_VERSION)$(if $(findstring dev,$(BATOCERA_SYSTEM_VERSION)),-$(BATOCERA_GIT_COMMIT)) $(BATOCERA_SYSTEM_DATE_TIME)

define BATOCERA_SYSTEM_INSTALL_TARGET_CMDS

	# version/arch
	mkdir -p $(TARGET_DIR)/usr/share/batocera
	echo -n '$(BATOCERA_ARCH)' > $(TARGET_DIR)/usr/share/batocera/batocera.arch
	echo '$(BATOCERA_SYSTEM_VERSION_WITH_DATE)' > $(TARGET_DIR)/usr/share/batocera/batocera.version

	# datainit
	mkdir -p $(TARGET_DIR)/usr/share/batocera/datainit/system
	cp $(BATOCERA_SYSTEM_PKGDIR)/batocera.conf $(TARGET_DIR)/usr/share/batocera/datainit/system

	# sysconfigs (default batocera.conf for boards)
	mkdir -p $(TARGET_DIR)/usr/share/batocera/sysconfigs
	if test -d $(BATOCERA_SYSTEM_PKGDIR)/sysconfigs/$(BATOCERA_ARCH); then \
		cp -pr $(BATOCERA_SYSTEM_PKGDIR)/sysconfigs/$(BATOCERA_ARCH)/* \
			$(TARGET_DIR)/usr/share/batocera/sysconfigs; \
	fi

	# mounts
	mkdir -p $(TARGET_DIR)/boot $(TARGET_DIR)/overlay $(TARGET_DIR)/userdata

	# variables
	mkdir -p $(TARGET_DIR)/etc/profile.d
	cp $(BATOCERA_SYSTEM_PKGDIR)/xdg.sh $(TARGET_DIR)/etc/profile.d/xdg.sh
	cp $(BATOCERA_SYSTEM_PKGDIR)/dbus.sh $(TARGET_DIR)/etc/profile.d/dbus.sh

	# list of modules that doesnt like suspend
	mkdir -p $(TARGET_DIR)/etc/pm/config.d
	echo 'SUSPEND_MODULES="rtw88_8822ce snd_pci_acp5x"' > $(TARGET_DIR)/etc/pm/config.d/config
endef

ifeq ($(BR2_PACKAGE_WAYLAND),y)
define BATOCERA_SYSTEM_INSTALL_WAYLAND
	cp $(BATOCERA_SYSTEM_PKGDIR)/wayland.sh $(TARGET_DIR)/etc/profile.d/wayland.sh
endef

BATOCERA_SYSTEM_POST_INSTALL_TARGET_HOOKS += BATOCERA_SYSTEM_INSTALL_WAYLAND
endif

define BATOCERA_SYSTEM_INSTALL_IMAGES_CMDS
	# batocera-boot.conf
	$(INSTALL) -D -m 0644 $(BATOCERA_SYSTEM_PKGDIR)/batocera-boot.conf $(BINARIES_DIR)/batocera-boot.conf
endef

$(eval $(generic-package))
