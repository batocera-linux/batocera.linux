################################################################################
#
# touchegg
#
################################################################################

TOUCHEGG_VERSION = 2.0.14
TOUCHEGG_SITE = $(call github,JoseExposito,touchegg,$(TOUCHEGG_VERSION))
TOUCHEGG_DEPENDENCIES = xapp_xinput pugixml cairo libinput xlib_libXtst

TOUCHEGG_CONF_OPTS += -DCMAKE_INSTALL_PREFIX=$(STAGING_DIR)/usr/ -DUSE_SYSTEMD=0

define TOUCHEGG_INSTALL_TARGET_CMDS
	 cp -f $(@D)/touchegg $(TARGET_DIR)/usr/bin
	 mkdir -p $(TARGET_DIR)/usr/share/touchegg
	 cp -f $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/utils/touchegg/touchegg.conf \
	  $(TARGET_DIR)/usr/share/touchegg/
	 mkdir -p $(TARGET_DIR)/etc/xdg
	 ln -sf /usr/share/touchegg $(TARGET_DIR)/etc/xdg/
endef

$(eval $(cmake-package))
