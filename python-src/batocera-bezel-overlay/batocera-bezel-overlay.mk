################################################################################
#
# batocera-bezel-overlay
#
################################################################################

BATOCERA_BEZEL_OVERLAY_VERSION=44.0
BATOCERA_BEZEL_OVERLAY_LICENSE=GPL
BATOCERA_BEZEL_OVERLAY_SETUP_TYPE=hatch
BATOCERA_BEZEL_OVERLAY_DEPENDENCIES=python3 python-pycairo python-gobject libgtk3

ifeq ($(BR2_PACKAGE_GTK_LAYER_SHELL),y)
BATOCERA_BEZEL_OVERLAY_DEPENDENCIES += gtk-layer-shell
endif

$(eval $(local-python-package))
