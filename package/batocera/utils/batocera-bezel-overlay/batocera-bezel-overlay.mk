################################################################################
#
# batocera-bezel-overlay
#
################################################################################

BATOCERA_BEZEL_OVERLAY_VERSION=44.0
BATOCERA_BEZEL_OVERLAY_LICENSE=GPL
BATOCERA_BEZEL_OVERLAY_SOURCE=
BATOCERA_BEZEL_OVERLAY_OVERRIDE_SRCDIR=$(BR2_EXTERNAL_BATOCERA_PATH)/python-src/batocera-bezel-overlay
BATOCERA_BEZEL_OVERLAY_OVERRIDE_SRCDIR_RSYNC_EXCLUSIONS=--exclude=".*" --exclude="**/__pycache__/" --exclude="dist"
BATOCERA_BEZEL_OVERLAY_SETUP_TYPE=hatch
BATOCERA_BEZEL_OVERLAY_DEPENDENCIES=python3 python-gobject libgtk3 gtk-layer-shell

$(eval $(python-package))
