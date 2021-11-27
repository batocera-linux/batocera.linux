################################################################################
#
# ROCKCHIP_RGA
#
################################################################################

# Version.: Commits on Oct 30, 2019
ROCKCHIP_RGA_VERSION = 72e7764a9fe358e6ad50eb1b21176cc95802c7fb
ROCKCHIP_RGA_SITE =  $(call github,batocera-linux,linux-rga,$(ROCKCHIP_RGA_VERSION))
ROCKCHIP_RGA_INSTALL_STAGING = YES

define ROCKCHIP_RGA_BUILD_CMDS
	mkdir -p $(@D)/include
	mkdir -p $(@D)/lib
	$(TARGET_CONFIGURE_OPTS) $(MAKE) -C $(@D) -f Makefile PROJECT_DIR=$(@D)
endef

define ROCKCHIP_RGA_INSTALL_TARGET_CMDS
	mkdir -p $(STAGING_DIR)/usr/include/rga/
	cp -r $(@D)/lib/librga.so $(TARGET_DIR)/usr/lib/
	cp -r $(@D)/lib/librga.so $(STAGING_DIR)/usr/lib/
	cp -r $(@D)/*.h $(STAGING_DIR)/usr/include/rga/
endef

$(eval $(generic-package))
