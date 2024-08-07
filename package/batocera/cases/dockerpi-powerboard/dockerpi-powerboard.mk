################################################################################
#
# dockerpi-powerboard
#
################################################################################
#Version: Commits on Feb 28, 2024
DOCKERPI_POWERBOARD_VERSION = 1e268b076bfb2bba0de053c780474239f4f88245
DOCKERPI_POWERBOARD_SITE = $(call github,geeekpi,dockerpi,$(DOCKERPI_POWERBOARD_VERSION))

ifeq ($(BR2_aarch64),y)
    DOCKERPI_POWERBOARD_ARCH = 64bit
    DOCKERPI_POWERBOARD_BINARY = powerboard64
else
    DOCKERPI_POWERBOARD_ARCH = 32bit
    DOCKERPI_POWERBOARD_BINARY = powerboard32
endif

define DOCKERPI_POWERBOARD_BUILD_CMDS
    $(TARGET_CC) -o \
        $(@D)/powerboard/src/$(DOCKERPI_POWERBOARD_ARCH)/$(DOCKERPI_POWERBOARD_BINARY) \
        $(@D)/powerboard/src/$(DOCKERPI_POWERBOARD_ARCH)/$(DOCKERPI_POWERBOARD_BINARY).c
endef

define DOCKERPI_POWERBOARD_INSTALL_TARGET_CMDS
    $(INSTALL) -D -m 0755 \
        $(@D)/powerboard/src/$(DOCKERPI_POWERBOARD_ARCH)/$(DOCKERPI_POWERBOARD_BINARY) \
        $(TARGET_DIR)/usr/sbin/$(DOCKERPI_POWERBOARD_BINARY)
endef

$(eval $(generic-package))
