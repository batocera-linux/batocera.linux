################################################################################
#
# wxwidgets
#
################################################################################

WXWIDGETS_VERSION = v3.2.4
WXWIDGETS_SITE = https://github.com/wxWidgets/wxWidgets
WXWIDGETS_DEPENDENCIES = zlib libpng jpeg gdk-pixbuf libgtk3 libglu
WXWIDGETS_SITE_METHOD = git
WXWIDGETS_GIT_SUBMODULES = YES
WXWIDGETS_DEPENDENCIES = host-libgtk3 libgtk3

WXWIDGETS_SUPPORTS_IN_SOURCE_BUILD = NO
WXWIDGETS_INSTALL_STAGING = YES

define WXWIDGETS_FIXUP_WXWIDGET_CONFIG
       ln -sf $(STAGING_DIR)/usr/lib/wx/config/*gtk3-unicode-* $(STAGING_DIR)/usr/bin/wx-config
	$(SED) 's%^prefix=.*%prefix=$(STAGING_DIR)/usr%' \
		$(STAGING_DIR)/usr/bin/wx-config
	$(SED) 's%^exec_prefix=.*%exec_prefix=$${prefix}%' \
		$(STAGING_DIR)/usr/bin/wx-config
endef

WXWIDGETS_POST_INSTALL_STAGING_HOOKS += WXWIDGETS_FIXUP_WXWIDGET_CONFIG

$(eval $(cmake-package))
