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
endef

define GAMECON_GPIO_RPI_BUILD_CMDS
	cp package/gamecon_gpio_rpi/gamecon_gpio_rpi.c $(@D)
	cp package/gamecon_gpio_rpi/Makefile $(@D)
        $(MAKE) -C $(@D) $(LINUX_MAKE_FLAGS) KERNELDIR=$(LINUX_DIR)
endef

define GAMECON_GPIO_RPI_INSTALL_TARGET_CMDS
        $(MAKE) -C $(@D) $(LINUX_MAKE_FLAGS) KERNELDIR=$(LINUX_DIR) modules_install
endef

$(eval $(generic-package))
