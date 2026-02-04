################################################################################
#
# wxwidgets
#
################################################################################

WXWIDGETS_VERSION = v3.3.1
WXWIDGETS_SITE = https://github.com/wxWidgets/wxWidgets
WXWIDGETS_SITE_METHOD = git
WXWIDGETS_GIT_SUBMODULES = YES

WXWIDGETS_DEPENDENCIES = gdk-pixbuf gst1-plugins-base gstreamer1 host-libgtk3
WXWIDGETS_DEPENDENCIES += jpeg libcurl libglu libgtk3 libpng libsecret pcre2
WXWIDGETS_DEPENDENCIES += sdl2 webp xz zlib

WXWIDGETS_SUPPORTS_IN_SOURCE_BUILD = NO
WXWIDGETS_INSTALL_STAGING = YES

WXWIDGETS_SERIES = $(shell echo $(WXWIDGETS_VERSION) | sed 's/^v//;s/\.[0-9]*$$//')

define WXWIDGETS_FIXUP_WXWIDGET_CONFIG
    # Explicitly target the version we want
    ln -sf $(STAGING_DIR)/usr/lib/wx/config/gtk3-unicode-$(WXWIDGETS_SERIES) \
           $(STAGING_DIR)/usr/bin/wx-config
    $(SED) 's%^prefix=.*%prefix=$(STAGING_DIR)/usr%' \
        $(STAGING_DIR)/usr/bin/wx-config
    $(SED) 's%^exec_prefix=.*%exec_prefix=$${prefix}%' \
        $(STAGING_DIR)/usr/bin/wx-config
endef

WXWIDGETS_POST_INSTALL_STAGING_HOOKS += WXWIDGETS_FIXUP_WXWIDGET_CONFIG

$(eval $(cmake-package))
