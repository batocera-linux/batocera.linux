################################################################################
#
# Xen
#
################################################################################

XEN_VERSION = 4.9.0
XEN_SITE = https://downloads.xenproject.org/release/xen/$(XEN_VERSION)
XEN_PATCH = \
	https://xenbits.xenproject.org/xsa/xsa226.patch \
	https://xenbits.xenproject.org/xsa/xsa227.patch \
	https://xenbits.xenproject.org/xsa/xsa228.patch \
	https://xenbits.xenproject.org/xsa/xsa230.patch \
	https://xenbits.xenproject.org/xsa/xsa231-4.9.patch \
	https://xenbits.xenproject.org/xsa/xsa232.patch \
	https://xenbits.xenproject.org/xsa/xsa233.patch \
	https://xenbits.xenproject.org/xsa/xsa234-4.9.patch \
	https://xenbits.xenproject.org/xsa/xsa235-4.9.patch \
	https://xenbits.xenproject.org/xsa/xsa245/0001-xen-page_alloc-Cover-memory-unreserved-after-boot-in.patch \
	https://xenbits.xenproject.org/xsa/xsa245/0002-xen-arm-Correctly-report-the-memory-region-in-the-du.patch

XEN_LICENSE = GPL-2.0
XEN_LICENSE_FILES = COPYING
XEN_DEPENDENCIES = host-acpica host-python

# Calculate XEN_ARCH
ifeq ($(ARCH),aarch64)
XEN_ARCH = arm64
else ifeq ($(ARCH),arm)
XEN_ARCH = arm32
endif

XEN_CONF_OPTS = --disable-ocamltools

XEN_CONF_ENV = PYTHON=$(HOST_DIR)/bin/python2
XEN_MAKE_ENV = \
	XEN_TARGET_ARCH=$(XEN_ARCH) \
	CROSS_COMPILE=$(TARGET_CROSS) \
	HOST_EXTRACFLAGS="-Wno-error" \
	$(TARGET_CONFIGURE_OPTS)

ifeq ($(BR2_PACKAGE_XEN_HYPERVISOR),y)
XEN_MAKE_OPTS += dist-xen
XEN_INSTALL_IMAGES = YES
define XEN_INSTALL_IMAGES_CMDS
	cp $(@D)/xen/xen $(BINARIES_DIR)
endef
else
XEN_CONF_OPTS += --disable-xen
endif

ifeq ($(BR2_PACKAGE_XEN_TOOLS),y)
XEN_DEPENDENCIES += dtc libaio libglib2 ncurses openssl pixman util-linux yajl
ifeq ($(BR2_PACKAGE_ARGP_STANDALONE),y)
XEN_DEPENDENCIES += argp-standalone
endif
XEN_INSTALL_TARGET_OPTS += DESTDIR=$(TARGET_DIR) install-tools
XEN_MAKE_OPTS += dist-tools
XEN_CONF_OPTS += --with-extra-qemuu-configure-args="--disable-sdl"

define XEN_INSTALL_INIT_SYSV
	mv $(TARGET_DIR)/etc/init.d/xencommons $(TARGET_DIR)/etc/init.d/S50xencommons
	mv $(TARGET_DIR)/etc/init.d/xen-watchdog $(TARGET_DIR)/etc/init.d/S50xen-watchdog
	mv $(TARGET_DIR)/etc/init.d/xendomains $(TARGET_DIR)/etc/init.d/S60xendomains
endef
else
XEN_INSTALL_TARGET = NO
XEN_CONF_OPTS += --disable-tools
endif

$(eval $(autotools-package))
