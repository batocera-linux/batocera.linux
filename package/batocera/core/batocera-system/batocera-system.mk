################################################################################
#
# batocera.linux System
#
################################################################################

BATOCERA_SYSTEM_SOURCE=

BATOCERA_SYSTEM_VERSION = 36-dev
BATOCERA_SYSTEM_DATE_TIME = $(shell date "+%Y/%m/%d %H:%M")
BATOCERA_SYSTEM_DATE = $(shell date "+%Y/%m/%d")
BATOCERA_SYSTEM_DEPENDENCIES = tzdata

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2837),y)
	BATOCERA_SYSTEM_ARCH=bcm2837
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RK3399),y)
	BATOCERA_SYSTEM_ARCH=rk3399
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RK3288),y)
	BATOCERA_SYSTEM_ARCH=rk3288
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_TRITIUM_H5),y)
	BATOCERA_SYSTEM_ARCH=tritium_h5
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_ORANGEPI_ZERO2),y)
	BATOCERA_SYSTEM_ARCH=orangepi_zero2
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_ORANGEPI_PC),y)
	BATOCERA_SYSTEM_ARCH=orangepi_pc
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_CHA),y)
	BATOCERA_SYSTEM_ARCH=cha
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_S812),y)
	BATOCERA_SYSTEM_ARCH=s812
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_S922X),y)
	BATOCERA_SYSTEM_ARCH=s922x
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RK3326),y)
	BATOCERA_SYSTEM_ARCH=rk3326
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RK3128),y)
	BATOCERA_SYSTEM_ARCH=rk3128
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_XU4),y)
	BATOCERA_SYSTEM_ARCH=odroidxu4
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_S905),y)
	BATOCERA_SYSTEM_ARCH=s905
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_S905GEN2),y)
	BATOCERA_SYSTEM_ARCH=s905gen2
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_S905GEN3),y)
	BATOCERA_SYSTEM_ARCH=s905gen3
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_S912),y)
	BATOCERA_SYSTEM_ARCH=s912
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_X86),y)
	BATOCERA_SYSTEM_ARCH=x86
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_X86_64),y)
	BATOCERA_SYSTEM_ARCH=x86_64
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_STEAMDECK),y)
	BATOCERA_SYSTEM_ARCH=steamdeck
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_PS4),y)
	BATOCERA_SYSTEM_ARCH=ps4
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_ZNVER2),y)
	BATOCERA_SYSTEM_ARCH=znver2
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2836),y)
	BATOCERA_SYSTEM_ARCH=bcm2836
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2835),y)
	BATOCERA_SYSTEM_ARCH=bcm2835
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPIZERO2),y)
    BATOCERA_SYSTEM_ARCH=rpizero2
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2711),y)
	BATOCERA_SYSTEM_ARCH=bcm2711
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_ODIN),y)
	BATOCERA_SYSTEM_ARCH=odin
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_ORANGEPI_3_LTS),y)
	BATOCERA_SYSTEM_ARCH=orangepi_3_lts
else
	BATOCERA_SYSTEM_ARCH=unknown
endif

ifneq (,$(findstring dev,$(BATOCERA_SYSTEM_VERSION)))
    BATOCERA_SYSTEM_COMMIT = "-$(shell cd $(BR2_EXTERNAL_BATOCERA_PATH) && git rev-parse --short HEAD)"
else
    BATOCERA_SYSTEM_COMMIT =
endif

define BATOCERA_SYSTEM_INSTALL_TARGET_CMDS

	# version/arch
	mkdir -p $(TARGET_DIR)/usr/share/batocera
	echo -n "$(BATOCERA_SYSTEM_ARCH)" > $(TARGET_DIR)/usr/share/batocera/batocera.arch
	echo $(BATOCERA_SYSTEM_VERSION)$(BATOCERA_SYSTEM_COMMIT) $(BATOCERA_SYSTEM_DATE_TIME) > $(TARGET_DIR)/usr/share/batocera/batocera.version

	# datainit
	mkdir -p $(TARGET_DIR)/usr/share/batocera/datainit/system
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/core/batocera-system/batocera.conf $(TARGET_DIR)/usr/share/batocera/datainit/system

	# batocera-boot.conf
	$(INSTALL) -D -m 0644 $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/core/batocera-system/batocera-boot.conf $(BINARIES_DIR)/batocera-boot.conf

	# sysconfigs (default batocera.conf for boards)
	mkdir -p $(TARGET_DIR)/usr/share/batocera/sysconfigs
        if test -d $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/core/batocera-system/sysconfigs/${BATOCERA_SYSTEM_ARCH}; then cp -pr $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/core/batocera-system/sysconfigs/${BATOCERA_SYSTEM_ARCH}/* $(TARGET_DIR)/usr/share/batocera/sysconfigs; fi

	# mounts
	mkdir -p $(TARGET_DIR)/boot $(TARGET_DIR)/overlay $(TARGET_DIR)/userdata

	# variables
	mkdir -p $(TARGET_DIR)/etc/profile.d
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/core/batocera-system/xdg.sh $(TARGET_DIR)/etc/profile.d/xdg.sh
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/core/batocera-system/dbus.sh $(TARGET_DIR)/etc/profile.d/dbus.sh

	# list of modules that doesnt like suspend
	mkdir -p $(TARGET_DIR)/etc/pm/config.d
	echo 'SUSPEND_MODULES="rtw88_8822ce snd_pci_acp5x"' > $(TARGET_DIR)/etc/pm/config.d/config
endef

$(eval $(generic-package))
