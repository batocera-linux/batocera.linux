################################################################################
#
# MF
#
################################################################################
# Version.: Commits on Oct 4, 2021
MF_VERSION = 680890e6f93d0b601a641c7fd69d5f124fd65538
MF_SITE = $(call github,liberodark,mf-install,$(MF_VERSION))
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
