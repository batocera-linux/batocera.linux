################################################################################
#
# logitech-trueforce
#
################################################################################

LOGITECH_TRUEFORCE_VERSION = v0.24.0
LOGITECH_TRUEFORCE_SITE = $(call github,mescon,logitech-trueforce-linux-driver,$(LOGITECH_TRUEFORCE_VERSION))
LOGITECH_TRUEFORCE_LICENSE = GPL-2.0, GPL-2.0+ (mainline/dd-lg4ff.c)
LOGITECH_TRUEFORCE_LICENSE_FILES = COPYING

# the module sources live in mainline/, it builds as hid-logitech-dd.ko and
# binds only the direct drive wheels (RS50, G PRO), so it coexists with the
# in-tree hid-logitech-hidpp. The G923 it also knows about is patched to be
# opt-in behind the g923 module parameter, since new-lg4ff drives that wheel
# here, which is why upstream's modprobe.d file is not installed either: it
# blacklists hid-logitech-new outright and would cost the G29/G27/DFGT/DFP
# their driver.
LOGITECH_TRUEFORCE_MODULE_SUBDIRS = mainline

define LOGITECH_TRUEFORCE_INSTALL_TARGET_CMDS
	$(INSTALL) -m 0644 -D $(@D)/udev/70-logitech-trueforce.rules \
		$(TARGET_DIR)/etc/udev/rules.d/70-logitech-trueforce.rules
endef

$(eval $(kernel-module))
$(eval $(generic-package))
