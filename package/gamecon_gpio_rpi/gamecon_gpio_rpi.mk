################################################################################
#
# GAMECON_GPIO_RPI
#
################################################################################
GAMECON_GPIO_RPI_VERSION = 1.0
GAMECON_GPIO_RPI_SOURCE = gamecon-gpio-rpi-dkms_$(GAMECON_GPIO_RPI_VERSION)_all.deb
GAMECON_GPIO_RPI_SITE = http://www.niksula.hut.fi/~mhiienka/Rpi

GAMECON_GPIO_RPI_DEPENDENCIES = linux

define GAMECON_GPIO_RPI_EXTRACT_CMDS
	cp package/gamecon_gpio_rpi/gamecon_gpio_rpi.c $(@D)
	cp package/gamecon_gpio_rpi/Makefile $(@D)
endef

# Needed because can't pass cflags to cc
define GAMECON_GPIO_RPI_RPI2_HOOK
        $(SED) "s/#define BCM2708_PERI_BASE 0x20000000/#define BCM2708_PERI_BASE 0x3F000000/g" $(@D)/gamecon_gpio_rpi.c
endef

ifeq ($(BR2_cortex_a7),y)
        GAMECON_GPIO_RPI_PRE_CONFIGURE_HOOKS += GAMECON_GPIO_RPI_RPI2_HOOK
endif

define GAMECON_GPIO_RPI_BUILD_CMDS
        $(MAKE) -C $(@D) $(LINUX_MAKE_FLAGS) KERNELDIR=$(LINUX_DIR)
endef

define GAMECON_GPIO_RPI_INSTALL_TARGET_CMDS
        $(MAKE) -C $(@D) $(LINUX_MAKE_FLAGS) KERNELDIR=$(LINUX_DIR) modules_install
endef

$(eval $(generic-package))
