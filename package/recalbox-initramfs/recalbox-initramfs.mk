################################################################################
#
# busybox_initramfs
#
################################################################################

RECALBOX_INITRAMFS_VERSION = 1.24.2
RECALBOX_INITRAMFS_SITE = http://www.busybox.net/downloads
RECALBOX_INITRAMFS_SOURCE = busybox-$(RECALBOX_INITRAMFS_VERSION).tar.bz2
RECALBOX_INITRAMFS_LICENSE = GPLv2
RECALBOX_INITRAMFS_LICENSE_FILES = LICENSE

RECALBOX_INITRAMFS_CFLAGS = $(TARGET_CFLAGS)
RECALBOX_INITRAMFS_LDFLAGS = $(TARGET_LDFLAGS)

RECALBOX_INITRAMFS_KCONFIG_FILE = "package/recalbox-initramfs/busybox.config"

INITRAMFS_DIR=$(BINARIES_DIR)/initramfs

# Allows the build system to tweak CFLAGS
RECALBOX_INITRAMFS_MAKE_ENV = \
	$(TARGET_MAKE_ENV) \
	CFLAGS="$(RECALBOX_INITRAMFS_CFLAGS)"
RECALBOX_INITRAMFS_MAKE_OPTS = \
	CC="$(TARGET_CC)" \
	ARCH=$(KERNEL_ARCH) \
	PREFIX="$(INITRAMFS_DIR)" \
	EXTRA_LDFLAGS="$(RECALBOX_INITRAMFS_LDFLAGS)" \
	CROSS_COMPILE="$(TARGET_CROSS)" \
	CONFIG_PREFIX="$(INITRAMFS_DIR)" \
	SKIP_STRIP=y

RECALBOX_INITRAMFS_KCONFIG_OPTS = $(RECALBOX_INITRAMFS_MAKE_OPTS)

define RECALBOX_INITRAMFS_BUILD_CMDS
	$(RECALBOX_INITRAMFS_MAKE_ENV) $(MAKE) $(RECALBOX_INITRAMFS_MAKE_OPTS) -C $(@D)
endef

ifeq ($(BR2_TARGET_UBOOT),y)
define RECALBOX_INITRAMFS_INSTALL_TARGET_CMDS
	mkdir -p $(INITRAMFS_DIR)
	cp package/recalbox-initramfs/init $(INITRAMFS_DIR)/init
	$(RECALBOX_INITRAMFS_MAKE_ENV) $(MAKE) $(RECALBOX_INITRAMFS_MAKE_OPTS) -C $(@D) install
	(cd $(INITRAMFS_DIR) && find . | cpio -H newc -o > $(BINARIES_DIR)/initrd)
ifeq ($(BR2_aarch64),y)
	(cd $(BINARIES_DIR) && mkimage -A arm64 -O linux -T ramdisk -C none -a 0 -e 0 -n initrd -d ./initrd ./uInitrd)
else
	(cd $(BINARIES_DIR) && mkimage -A arm -O linux -T ramdisk -C none -a 0 -e 0 -n initrd -d ./initrd ./uInitrd)
endif
endef
else
define RECALBOX_INITRAMFS_INSTALL_TARGET_CMDS
	mkdir -p $(INITRAMFS_DIR)
	cp package/recalbox-initramfs/init $(INITRAMFS_DIR)/init
	$(RECALBOX_INITRAMFS_MAKE_ENV) $(MAKE) $(RECALBOX_INITRAMFS_MAKE_OPTS) -C $(@D) install
	(cd $(INITRAMFS_DIR) && find . | cpio -H newc -o | gzip -9 > $(BINARIES_DIR)/initrd.gz)
endef
endif


$(eval $(kconfig-package))
