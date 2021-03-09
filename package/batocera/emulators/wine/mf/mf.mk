################################################################################
#
# MF
#
################################################################################

MF_VERSION = d363dce66f9731611efe71a8f78d01f99630874d
MF_SITE = $(call github,z0z0z,mf-install,$(MF_VERSION))
MF_LICENSE = zlib/libpng

define MF_EXTRACT_CMDS
	mkdir -p $(@D)/target && cd $(@D)/target && tar xf $(DL_DIR)/$(MF_DL_SUBDIR)/$(MF_SOURCE)
endef

define MF_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/usr/wine/mf
	$(INSTALL) -D $(@D)/target/mf-install-$(MF_VERSION)/mf-install.sh $(TARGET_DIR)/usr/wine/mf/mf-install.sh
	cp -pr $(@D)/target/mf-install-$(MF_VERSION)/*.reg $(TARGET_DIR)/usr/wine/mf/
	cp -pr $(@D)/target/mf-install-$(MF_VERSION)/system32 $(TARGET_DIR)/usr/wine/mf/
	cp -pr $(@D)/target/mf-install-$(MF_VERSION)/syswow64 $(TARGET_DIR)/usr/wine/mf/
endef

$(eval $(generic-package))
