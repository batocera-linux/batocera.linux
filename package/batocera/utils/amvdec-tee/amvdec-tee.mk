################################################################################
#
# amvdec-tee
#
################################################################################

AMVDEC_TEE_VERSION = 1d7e8009cce1692fef04a729e859e8602b8eec9e
AMVDEC_TEE_SITE = $(call github,LibreELEC,amvdec-tee,$(AMVDEC_TEE_VERSION))
AMVDEC_TEE_LICENSE = GPL-2.0-only
AMVDEC_TEE_LICENSE_FILES = LICENSE
AMVDEC_TEE_DEPENDENCIES = optee-client

define AMVDEC_TEE_BUILD_CMDS
	$(TARGET_MAKE_ENV) $(MAKE) -C $(@D) $(TARGET_CONFIGURE_OPTS)
endef

define AMVDEC_TEE_INSTALL_TARGET_CMDS
	$(TARGET_MAKE_ENV) $(MAKE) -C $(@D) DESTDIR=$(TARGET_DIR) install
	$(INSTALL) -D -m 0755 $(AMVDEC_TEE_PKGDIR)/S31amvdec-tee \
		$(TARGET_DIR)/etc/init.d/S31amvdec-tee
endef

$(eval $(generic-package))
