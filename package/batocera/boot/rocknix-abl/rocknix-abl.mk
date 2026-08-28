################################################################################
#
# rocknix-abl
#
################################################################################

ROCKNIX_ABL_VERSION = 1.1.8
ROCKNIX_ABL_SOURCE = rocknix-abl-v$(ROCKNIX_ABL_VERSION).tar.gz
ROCKNIX_ABL_SITE = https://github.com/ROCKNIX/abl/releases/download/v$(ROCKNIX_ABL_VERSION)

ROCKNIX_ABL_DEPENDENCIES = pv

# Handle sm8650 in future
ROCKNIX_ABL_MODEL = $(call UPPERCASE,$(BATOCERA_ARCH))

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
