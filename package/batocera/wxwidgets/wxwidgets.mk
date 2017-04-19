################################################################################
#
# WXWIDGETS
#
################################################################################

WXWIDGETS_VERSION = v3.1.0
WXWIDGETS_SITE = $(call github,wxWidgets,wxWidgets,$(WXWIDGETS_VERSION))
WXWIDGETS_DEPENDENCIES = zlib libpng jpeg gdk-pixbuf libgtk2
WXWIDGETS_INSTALL_STAGING = YES

define WXWIDGETS_FIXUP_WXWIDGET_CONFIG
       ln -sf $(STAGING_DIR)/usr/lib/wx/config/x86_64-buildroot-linux-gnu-gtk2-unicode-3.1 $(STAGING_DIR)/usr/bin/wx-config
	$(SED) 's%^prefix=.*%prefix=$(STAGING_DIR)/usr%' \
		$(STAGING_DIR)/usr/bin/wx-config
	$(SED) 's%^exec_prefix=.*%exec_prefix=$${prefix}%' \
		$(STAGING_DIR)/usr/bin/wx-config
endef

define WXWIDGETS_REMOVE_WXWIDGETS_CONFIG
	rm -f $(TARGET_DIR)/usr/bin/wx-config
	rm -rf $(TARGET_DIR)/usr/lib/wx/config
endef

WXWIDGETS_POST_INSTALL_TARGET_HOOKS += WXWIDGETS_REMOVE_WXWIDGETS_CONFIG
WXWIDGETS_POST_INSTALL_STAGING_HOOKS += WXWIDGETS_FIXUP_WXWIDGET_CONFIG

$(eval $(autotools-package))
