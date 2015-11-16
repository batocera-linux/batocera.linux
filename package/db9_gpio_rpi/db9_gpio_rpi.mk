################################################################################
#
# DB9_GPIO_RPI
#
################################################################################
DB9_GPIO_RPI_VERSION = 1.0
DB9_GPIO_RPI_SOURCE = db9-gpio-rpi-dkms_$(DB9_GPIO_RPI_VERSION)_all.deb
DB9_GPIO_RPI_SITE = http://www.niksula.hut.fi/~mhiienka/Rpi

DB9_GPIO_RPI_DEPENDENCIES = linux

define DB9_GPIO_RPI_EXTRACT_CMDS
endef

define DB9_GPIO_RPI_BUILD_CMDS
	cp package/db9_gpio_rpi/db9_gpio_rpi.c $(@D)
	cp package/db9_gpio_rpi/Makefile $(@D)
        $(MAKE) -C $(@D) $(LINUX_MAKE_FLAGS) KERNELDIR=$(LINUX_DIR)
endef

define DB9_GPIO_RPI_INSTALL_TARGET_CMDS
        $(MAKE) -C $(@D) $(LINUX_MAKE_FLAGS) KERNELDIR=$(LINUX_DIR) modules_install
endef

$(eval $(generic-package))
