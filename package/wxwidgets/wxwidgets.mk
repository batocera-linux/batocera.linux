################################################################################
#
# WXWIDGETS
#
################################################################################

WXWIDGETS_VERSION = v3.1.0
WXWIDGETS_SITE = $(call github,wxWidgets,wxWidgets,$(WXWIDGETS_VERSION))
WXWIDGETS_DEPENDENCIES = zlib libpng jpeg gdk-pixbuf libgtk2
WXWIDGETS_INSTALL_STAGING = YES

$(eval $(autotools-package))
