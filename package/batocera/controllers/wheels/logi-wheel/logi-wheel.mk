################################################################################
#
# logi-wheel
#
################################################################################

LOGI_WHEEL_VERSION = v0.24.0
LOGI_WHEEL_SITE = $(call github,mescon,logitech-trueforce-linux-driver,$(LOGI_WHEEL_VERSION))
LOGI_WHEEL_LICENSE = GPL-2.0, GPL-3.0+ (logi-wheel-gui), LGPL-2.1+ (libtrueforce)
LOGI_WHEEL_LICENSE_FILES = COPYING userspace/libtrueforce/COPYING

# the settings apps are a cargo workspace inside the logitech-trueforce
# driver repository, the kernel module itself is built by that package
LOGI_WHEEL_SUBDIR = userspace/logi-wheel

LOGI_WHEEL_CARGO_MODE = $(if $(BR2_ENABLE_DEBUG),debug,release)
# cargo builds in the workspace, which _SUBDIR puts below $(@D)
LOGI_WHEEL_BIN_DIR = $(LOGI_WHEEL_SRCDIR)/target/$(RUSTC_TARGET_NAME)/$(LOGI_WHEEL_CARGO_MODE)

# build only what we install: logi-wheel-core is a library the front ends
# pull in, and logi-wheel-gui is built separately below
#   logi-ffb     force feedback proxy for the DirectInput games that need
#                PROTON_ENABLE_HIDRAW=1, where wine reads the wheel's HID
#                descriptor itself and finds no PID collection in it
#   logi-tf-sim  TrueForce daemon fed by the UDP telemetry of a few PC
#                titles, started and configured from the settings apps
LOGI_WHEEL_CARGO_BUILD_OPTS = -p logi-wheel-tui -p logi-ffb -p logi-tf-sim

# logi-tf-sim links userspace/libtrueforce statically, and its build script
# runs the library's own makefile when the archive is missing: that call
# would get the host compiler, since cargo exports no CC for the target.
# Build it for the target here instead, the build script then finds the
# archive in place and leaves it alone.
define LOGI_WHEEL_BUILD_LIBTRUEFORCE
	$(TARGET_MAKE_ENV) $(MAKE) -C $(@D)/userspace/libtrueforce \
		CC="$(TARGET_CC)" AR="$(TARGET_AR)" \
		CFLAGS="$(TARGET_CFLAGS) -fPIC" \
		libtrueforce.a
endef
LOGI_WHEEL_PRE_BUILD_HOOKS += LOGI_WHEEL_BUILD_LIBTRUEFORCE

define LOGI_WHEEL_INSTALL_TARGET_CMDS
	$(INSTALL) -D -m 0755 $(LOGI_WHEEL_BIN_DIR)/logi-wheel \
		$(TARGET_DIR)/usr/bin/logi-wheel
	$(INSTALL) -D -m 0755 $(LOGI_WHEEL_BIN_DIR)/logi-ffb \
		$(TARGET_DIR)/usr/bin/logi-ffb
	$(INSTALL) -D -m 0755 $(LOGI_WHEEL_BIN_DIR)/logi-tf-sim \
		$(TARGET_DIR)/usr/bin/logi-tf-sim
endef

# the Slint desktop app, launched from the desktop mode as
# logi-wheel-config (see batocera-desktopapps)
ifeq ($(BR2_PACKAGE_LOGI_WHEEL_GUI),y)
LOGI_WHEEL_DEPENDENCIES += fontconfig libxkbcommon xlib_libX11
LOGI_WHEEL_CARGO_BUILD_OPTS += -p logi-wheel-gui

define LOGI_WHEEL_INSTALL_GUI
	$(INSTALL) -D -m 0755 $(LOGI_WHEEL_BIN_DIR)/logi-wheel-gui \
		$(TARGET_DIR)/usr/bin/logi-wheel-gui
endef
LOGI_WHEEL_POST_INSTALL_TARGET_HOOKS += LOGI_WHEEL_INSTALL_GUI
endif

$(eval $(cargo-package))
