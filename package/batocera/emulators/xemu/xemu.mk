################################################################################
#
# XEMU
#
################################################################################

# Daily build
XEMU_VERSION = build-202105250704
XEMU_SITE = https://github.com/mborgerson/xemu.git
XEMU_SITE_METHOD=git
XEMU_GIT_SUBMODULES=YES
XEMU_LICENSE = GPLv2
XEMU_DEPENDENCIES = sdl2

XEMU_EXTRA_DOWNLOADS = https://github.com/mborgerson/xemu-hdd-image/releases/download/1.0/xbox_hdd.qcow2.zip

XEMU_CONF_ENV += PATH="/x86_64/host/x86_64-buildroot-linux-gnu/sysroot/usr/bin:$$PATH"

XEMU_CONF_OPTS += --target-list=i386-softmmu
XEMU_CONF_OPTS += --cross-prefix="$(STAGING_DIR)"
XEMU_CONF_OPTS += --extra-cflags="-DXBOX=1 -O3 -Wno-error=redundant-decls -Wno-error=unused-but-set-variable"
XEMU_CONF_OPTS += --extra-ldflags=""
XEMU_CONF_OPTS += --enable-sdl
XEMU_CONF_OPTS += --enable-opengl
XEMU_CONF_OPTS += --enable-trace-backends="nop"
XEMU_CONF_OPTS += --disable-kvm
XEMU_CONF_OPTS += --disable-xen
XEMU_CONF_OPTS += --disable-werror
XEMU_CONF_OPTS += --disable-curl
XEMU_CONF_OPTS += --disable-vnc
XEMU_CONF_OPTS += --disable-vnc-sasl
XEMU_CONF_OPTS += --disable-docs
XEMU_CONF_OPTS += --disable-tools
XEMU_CONF_OPTS += --disable-guest-agent
XEMU_CONF_OPTS += --disable-tpm
XEMU_CONF_OPTS += --disable-live-block-migration
XEMU_CONF_OPTS += --disable-rdma
XEMU_CONF_OPTS += --disable-replication
XEMU_CONF_OPTS += --disable-capstone
XEMU_CONF_OPTS += --disable-fdt
XEMU_CONF_OPTS += --disable-libiscsi
XEMU_CONF_OPTS += --disable-spice
XEMU_CONF_OPTS += --disable-user
XEMU_CONF_OPTS += --disable-stack-protector
XEMU_CONF_OPTS += --disable-glusterfs
XEMU_CONF_OPTS += --disable-gtk
XEMU_CONF_OPTS += --disable-curses
XEMU_CONF_OPTS += --disable-gnutls
XEMU_CONF_OPTS += --disable-nettle
XEMU_CONF_OPTS += --disable-gcrypt
XEMU_CONF_OPTS += --disable-crypto-afalg
XEMU_CONF_OPTS += --disable-virglrenderer
XEMU_CONF_OPTS += --disable-vhost-net
XEMU_CONF_OPTS += --disable-vhost-crypto
XEMU_CONF_OPTS += --disable-vhost-vsock
XEMU_CONF_OPTS += --disable-vhost-user
XEMU_CONF_OPTS += --disable-virtfs
XEMU_CONF_OPTS += --disable-snappy
XEMU_CONF_OPTS += --disable-bzip2
XEMU_CONF_OPTS += --disable-vde
XEMU_CONF_OPTS += --disable-libxml2
XEMU_CONF_OPTS += --disable-seccomp
XEMU_CONF_OPTS += --disable-numa
XEMU_CONF_OPTS += --disable-lzo
XEMU_CONF_OPTS += --disable-smartcard
XEMU_CONF_OPTS += --disable-usb-redir
XEMU_CONF_OPTS += --disable-bochs
XEMU_CONF_OPTS += --disable-cloop
XEMU_CONF_OPTS += --disable-dmg
XEMU_CONF_OPTS += --disable-vdi
XEMU_CONF_OPTS += --disable-vvfat
XEMU_CONF_OPTS += --disable-qcow1
XEMU_CONF_OPTS += --disable-qed
XEMU_CONF_OPTS += --disable-parallels
XEMU_CONF_OPTS += --disable-sheepdog
XEMU_CONF_OPTS += --disable-blobs
XEMU_CONF_OPTS += --disable-hax
XEMU_CONF_OPTS += --disable-hvf
XEMU_CONF_OPTS += --disable-whpx
XEMU_CONF_OPTS += --without-default-devices

define XEMU_CONFIGURE_CMDS
	cd $(@D) && $(TARGET_CONFIGURE_OPTS) ./configure $(XEMU_CONF_OPTS)
endef

define XEMU_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" \
		CC_FOR_BUILD="$(TARGET_CC)" GCC_FOR_BUILD="$(TARGET_CC)" \
		CXX_FOR_BUILD="$(TARGET_CXX)" LD_FOR_BUILD="$(TARGET_LD)" \
                CROSS_COMPILE="$(STAGING_DIR)/usr/bin/" \
                PREFIX="/x86_64/host/x86_64-buildroot-linux-gnu/sysroot/" \
                PKG_CONFIG="/x86_64/host/x86_64-buildroot-linux-gnu/sysroot/usr/bin/pkg-config" \
		$(MAKE) -C $(@D) V=1
endef

define XEMU_INSTALL_TARGET_CMDS
	# Binaries
	cp $(@D)/build/qemu-system-i386 $(TARGET_DIR)/usr/bin/xemu

	# XEmu app data
	mkdir -p $(TARGET_DIR)/usr/share/xemu/data
	cp $(@D)/data/* $(TARGET_DIR)/usr/share/xemu/data/
	$(UNZIP) -ob $(XEMU_DL_DIR)/xbox_hdd.qcow2.zip xbox_hdd.qcow2 -d $(TARGET_DIR)/usr/share/xemu/data
endef

define XEMU_EVMAPY
	mkdir -p $(TARGET_DIR)/usr/share/evmapy
	cp $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/emulators/xemu/xbox.xemu.keys $(TARGET_DIR)/usr/share/evmapy
endef

XEMU_POST_INSTALL_TARGET_HOOKS += XEMU_EVMAPY

$(eval $(autotools-package))
