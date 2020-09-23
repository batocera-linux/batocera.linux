################################################################################
#
# LIBRGA
#
################################################################################

# Version.: Commits on Oct 30, 2019
LIBRGA_VERSION = 72e7764a9fe358e6ad50eb1b21176cc95802c7fb
LIBRGA_SITE =  $(call github,oiramario,linux-rga,$(LIBRGA_VERSION))
LIBRGA_INSTALL_STAGING = YES

define LIBRGA_BUILD_CMDS
	mkdir -p $(@D)/include
	mkdir -p $(@D)/lib
	$(TARGET_CONFIGURE_OPTS) $(MAKE) -C $(@D) -f Makefile PROJECT_DIR=$(@D)
endef

define LIBRGA_INSTALL_TARGET_CMDS
	mkdir -p $(STAGING_DIR)/usr/include/rga/
	cp -r $(@D)/lib/librga.so $(TARGET_DIR)/usr/lib/
	cp -r $(@D)/lib/librga.so $(STAGING_DIR)/usr/lib/
	cp -r $(@D)/*.h $(STAGING_DIR)/usr/include/rga/
endef

$(eval $(generic-package))
