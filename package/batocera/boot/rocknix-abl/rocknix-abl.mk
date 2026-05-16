################################################################################
#
# rocknix-abl
#
################################################################################

ROCKNIX_ABL_VERSION = 1.0.0
ROCKNIX_ABL_SOURCE = rocknix-abl-v$(ROCKNIX_ABL_VERSION).tar.gz
ROCKNIX_ABL_SITE = https://github.com/ROCKNIX/abl/releases/download/v$(ROCKNIX_ABL_VERSION)

ROCKNIX_ABL_DEPENDENCIES = pv

# Handle sm8650 in future
ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_SM8250),y)
ROCKNIX_ABL_MODEL = SM8250
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_SM8550),y)
ROCKNIX_ABL_MODEL = SM8550
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_SM6115),y)
ROCKNIX_ABL_MODEL = SM6115
endif

define ROCKNIX_ABL_INSTALL_TARGET_CMDS
	$(if $(ROCKNIX_ABL_MODEL), \
		mkdir -p $(TARGET_DIR)/usr/share/bootloader/rocknix_abl ; \
		$(INSTALL) -m 0644 $(@D)/abl_signed-$(ROCKNIX_ABL_MODEL).elf \
			$(TARGET_DIR)/usr/share/bootloader/rocknix_abl/ ; \
		$(INSTALL) -m 0644 $(@D)/abl_signed-$(ROCKNIX_ABL_MODEL).elf.sha256 \
			$(TARGET_DIR)/usr/share/bootloader/rocknix_abl/ ; \
		$(INSTALL) -D -m 0755 $(ROCKNIX_ABL_PKGDIR)/updateabl \
			$(TARGET_DIR)/usr/bin/updateabl
	)
endef

$(eval $(generic-package))
