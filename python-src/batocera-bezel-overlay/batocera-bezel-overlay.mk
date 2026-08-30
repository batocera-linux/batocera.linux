################################################################################
#
# batocera-bezel-overlay
#
################################################################################

BATOCERA_BEZEL_OVERLAY_VERSION=44.0
BATOCERA_BEZEL_OVERLAY_LICENSE=GPL
BATOCERA_BEZEL_OVERLAY_SETUP_TYPE=hatch
BATOCERA_BEZEL_OVERLAY_DEPENDENCIES=python3 python-gobject libgtk3 gtk-layer-shell

$(eval $(local-python-package))
