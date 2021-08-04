################################################################################
#
# busybox_initramfs
#
################################################################################

BATOCERA_INITRAMFS_VERSION = 1.24.2
BATOCERA_INITRAMFS_SITE = http://www.busybox.net/downloads
BATOCERA_INITRAMFS_SOURCE = busybox-$(BATOCERA_INITRAMFS_VERSION).tar.bz2
BATOCERA_INITRAMFS_LICENSE = GPLv2
BATOCERA_INITRAMFS_LICENSE_FILES = LICENSE

BATOCERA_INITRAMFS_CFLAGS = $(TARGET_CFLAGS)
BATOCERA_INITRAMFS_LDFLAGS = $(TARGET_LDFLAGS)

BATOCERA_INITRAMFS_KCONFIG_FILE = $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/boot/batocera-initramfs/busybox.config

INITRAMFS_DIR=$(BINARIES_DIR)/initramfs

# Allows the build system to tweak CFLAGS
BATOCERA_INITRAMFS_MAKE_ENV = \
	$(TARGET_MAKE_ENV) \
	CFLAGS="$(BATOCERA_INITRAMFS_CFLAGS)"
BATOCERA_INITRAMFS_MAKE_OPTS = \
	CC="$(TARGET_CC)" \
	ARCH=$(KERNEL_ARCH) \
	PREFIX="$(INITRAMFS_DIR)" \
	EXTRA_LDFLAGS="$(BATOCERA_INITRAMFS_LDFLAGS)" \
	CROSS_COMPILE="$(TARGET_CROSS)" \
	CONFIG_PREFIX="$(INITRAMFS_DIR)" \
	SKIP_STRIP=n

BATOCERA_INITRAMFS_KCONFIG_OPTS = $(BATOCERA_INITRAMFS_MAKE_OPTS)

define BATOCERA_INITRAMFS_BUILD_CMDS
	$(BATOCERA_INITRAMFS_MAKE_ENV) $(MAKE) $(BATOCERA_INITRAMFS_MAKE_OPTS) -C $(@D)
endef

ifeq ($(BR2_aarch64)$(BR2_TOOLCHAIN_OPTIONAL_LINARO_AARCH64),y)
BATOCERA_INITRAMFS_INITRDA=arm64
else
BATOCERA_INITRAMFS_INITRDA=arm
endif

define BATOCERA_INITRAMFS_INSTALL_TARGET_CMDS
	mkdir -p $(INITRAMFS_DIR)
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/boot/batocera-initramfs/init $(INITRAMFS_DIR)/init
	$(BATOCERA_INITRAMFS_MAKE_ENV) $(MAKE) $(BATOCERA_INITRAMFS_MAKE_OPTS) -C $(@D) install
	(cd $(INITRAMFS_DIR) && find . | cpio -H newc -o > $(BINARIES_DIR)/initrd)
	(cd $(BINARIES_DIR) && mkimage -A $(BATOCERA_INITRAMFS_INITRDA) -O linux -T ramdisk -C none -a 0 -e 0 -n initrd -d ./initrd ./uInitrd)
	(cd $(INITRAMFS_DIR) && find . | cpio -H newc -o | gzip -9 > $(BINARIES_DIR)/initrd.gz)
endef

$(eval $(kconfig-package))
