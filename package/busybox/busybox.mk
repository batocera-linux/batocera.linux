################################################################################
#
# busybox
#
################################################################################

BUSYBOX_VERSION = 1.31.0
BUSYBOX_SITE = http://www.busybox.net/downloads
BUSYBOX_SOURCE = busybox-$(BUSYBOX_VERSION).tar.bz2
BUSYBOX_LICENSE = GPL-2.0
BUSYBOX_LICENSE_FILES = LICENSE

define BUSYBOX_HELP_CMDS
	@echo '  busybox-menuconfig     - Run BusyBox menuconfig'
endef

BUSYBOX_CFLAGS = \
	$(TARGET_CFLAGS)

BUSYBOX_LDFLAGS = \
	$(TARGET_LDFLAGS)

# Packages that provide commands that may also be busybox applets:
BUSYBOX_DEPENDENCIES = \
	$(if $(BR2_PACKAGE_ATTR),attr) \
	$(if $(BR2_PACKAGE_BASH),bash) \
	$(if $(BR2_PACKAGE_BC),bc) \
	$(if $(BR2_PACKAGE_BINUTILS),binutils) \
	$(if $(BR2_PACKAGE_COREUTILS),coreutils) \
	$(if $(BR2_PACKAGE_CPIO),cpio) \
	$(if $(BR2_PACKAGE_DCRON),dcron) \
	$(if $(BR2_PACKAGE_DEBIANUTILS),debianutils) \
	$(if $(BR2_PACKAGE_DIFFUTILS),diffutils) \
	$(if $(BR2_PACKAGE_DOS2UNIX),dos2unix) \
	$(if $(BR2_PACKAGE_DOSFSTOOLS),dosfstools) \
	$(if $(BR2_PACKAGE_E2FSPROGS),e2fsprogs) \
	$(if $(BR2_PACKAGE_FBSET),fbset) \
	$(if $(BR2_PACKAGE_GAWK),gawk) \
	$(if $(BR2_PACKAGE_GREP),grep) \
	$(if $(BR2_PACKAGE_GZIP),gzip) \
	$(if $(BR2_PACKAGE_I2C_TOOLS),i2c-tools) \
	$(if $(BR2_PACKAGE_IFENSLAVE),ifenslave) \
	$(if $(BR2_PACKAGE_IFPLUGD),ifplugd) \
	$(if $(BR2_PACKAGE_IFUPDOWN),ifupdown) \
	$(if $(BR2_PACKAGE_IPROUTE2),iproute2) \
	$(if $(BR2_PACKAGE_IPUTILS),iputils) \
	$(if $(BR2_PACKAGE_KMOD),kmod) \
	$(if $(BR2_PACKAGE_LESS),less) \
	$(if $(BR2_PACKAGE_LSOF),lsof) \
	$(if $(BR2_PACKAGE_MTD),mtd) \
	$(if $(BR2_PACKAGE_NET_TOOLS),net-tools) \
	$(if $(BR2_PACKAGE_NETCAT),netcat) \
	$(if $(BR2_PACKAGE_NETCAT_OPENSBSD),netcat-openbsd) \
	$(if $(BR2_PACKAGE_NMAP),nmap) \
	$(if $(BR2_PACKAGE_NTP),ntp) \
	$(if $(BR2_PACKAGE_PCIUTILS),pciutils) \
	$(if $(BR2_PACKAGE_PROCPS_NG),procps-ng) \
	$(if $(BR2_PACKAGE_PSMISC),psmisc) \
	$(if $(BR2_PACKAGE_START_STOP_DAEMON),start-stop-daemon) \
	$(if $(BR2_PACKAGE_SYSKLOGD),sysklogd) \
	$(if $(BR2_PACKAGE_SYSTEMD),systemd) \
	$(if $(BR2_PACKAGE_SYSVINIT),sysvinit) \
	$(if $(BR2_PACKAGE_TAR),tar) \
	$(if $(BR2_PACKAGE_TFTPD),tftpd) \
	$(if $(BR2_PACKAGE_TRACEROUTE),traceroute) \
	$(if $(BR2_PACKAGE_UNZIP),unzip) \
	$(if $(BR2_PACKAGE_USBUTILS),usbutils) \
	$(if $(BR2_PACKAGE_UTIL_LINUX),util-linux) \
	$(if $(BR2_PACKAGE_VIM),vim) \
	$(if $(BR2_PACKAGE_WGET),wget) \
	$(if $(BR2_PACKAGE_WHOIS),whois)

# Link against libtirpc if available so that we can leverage its RPC
# support for NFS mounting with BusyBox
ifeq ($(BR2_PACKAGE_LIBTIRPC),y)
BUSYBOX_DEPENDENCIES += libtirpc host-pkgconf
BUSYBOX_CFLAGS += "`$(PKG_CONFIG_HOST_BINARY) --cflags libtirpc`"
# Don't use LDFLAGS for -ltirpc, because LDFLAGS is used for
# the non-final link of modules as well.
BUSYBOX_CFLAGS_busybox += "`$(PKG_CONFIG_HOST_BINARY) --libs libtirpc`"
endif

BUSYBOX_BUILD_CONFIG = $(BUSYBOX_DIR)/.config
# Allows the build system to tweak CFLAGS
BUSYBOX_MAKE_ENV = \
	$(TARGET_MAKE_ENV) \
	CFLAGS="$(BUSYBOX_CFLAGS)" \
	CFLAGS_busybox="$(BUSYBOX_CFLAGS_busybox)"

ifeq ($(BR2_REPRODUCIBLE),y)
BUSYBOX_MAKE_ENV += \
	KCONFIG_NOTIMESTAMP=1
endif

BUSYBOX_MAKE_OPTS = \
	CC="$(TARGET_CC)" \
	ARCH=$(KERNEL_ARCH) \
	PREFIX="$(TARGET_DIR)" \
	EXTRA_LDFLAGS="$(BUSYBOX_LDFLAGS)" \
	CROSS_COMPILE="$(TARGET_CROSS)" \
	CONFIG_PREFIX="$(TARGET_DIR)" \
	SKIP_STRIP=y

ifndef BUSYBOX_CONFIG_FILE
BUSYBOX_CONFIG_FILE = $(call qstrip,$(BR2_PACKAGE_BUSYBOX_CONFIG))
endif

BUSYBOX_KCONFIG_FILE = $(BUSYBOX_CONFIG_FILE)
BUSYBOX_KCONFIG_FRAGMENT_FILES = $(call qstrip,$(BR2_PACKAGE_BUSYBOX_CONFIG_FRAGMENT_FILES))
BUSYBOX_KCONFIG_EDITORS = menuconfig xconfig gconfig
BUSYBOX_KCONFIG_OPTS = $(BUSYBOX_MAKE_OPTS)

ifeq ($(BR2_PACKAGE_BUSYBOX_INDIVIDUAL_BINARIES),y)
define BUSYBOX_PERMISSIONS
# Set permissions on all applets with BB_SUID_REQUIRE and BB_SUID_MAYBE.
# 12 Applets are pulled from applets.h using grep command :
#  grep -r -e "APPLET.*BB_SUID_REQUIRE\|APPLET.*BB_SUID_MAYBE" \
#  $(@D)/include/applets.h
# These applets are added to the device table and the makedev file
# ignores the files with type 'F' ( optional files).
	/usr/bin/wall 			 F 4755 0  0 - - - - -
	/bin/ping 			 F 4755 0  0 - - - - -
	/bin/ping6 			 F 4755 0  0 - - - - -
	/usr/bin/crontab 		 F 4755 0  0 - - - - -
	/sbin/findfs 			 F 4755 0  0 - - - - -
	/bin/login 			 F 4755 0  0 - - - - -
	/bin/mount 			 F 4755 0  0 - - - - -
	/usr/bin/passwd 		 F 4755 0  0 - - - - -
	/bin/su 			 F 4755 0  0 - - - - -
	/usr/bin/traceroute 		 F 4755 0  0 - - - - -
	/usr/bin/traceroute6 		 F 4755 0  0 - - - - -
	/usr/bin/vlock 			 F 4755 0  0 - - - - -
endef
else
define BUSYBOX_PERMISSIONS
	/bin/busybox                     f 4755 0  0 - - - - -
endef
endif

# If mdev will be used for device creation enable it and copy S10mdev to /etc/init.d
ifeq ($(BR2_ROOTFS_DEVICE_CREATION_DYNAMIC_MDEV),y)
define BUSYBOX_INSTALL_MDEV_SCRIPT
	$(INSTALL) -D -m 0755 package/busybox/S10mdev \
		$(TARGET_DIR)/etc/init.d/S10mdev
endef
define BUSYBOX_INSTALL_MDEV_CONF
	$(INSTALL) -D -m 0644 package/busybox/mdev.conf \
		$(TARGET_DIR)/etc/mdev.conf
endef
define BUSYBOX_SET_MDEV
	$(call KCONFIG_ENABLE_OPT,CONFIG_MDEV,$(BUSYBOX_BUILD_CONFIG))
	$(call KCONFIG_ENABLE_OPT,CONFIG_FEATURE_MDEV_CONF,$(BUSYBOX_BUILD_CONFIG))
	$(call KCONFIG_ENABLE_OPT,CONFIG_FEATURE_MDEV_EXEC,$(BUSYBOX_BUILD_CONFIG))
	$(call KCONFIG_ENABLE_OPT,CONFIG_FEATURE_MDEV_LOAD_FIRMWARE,$(BUSYBOX_BUILD_CONFIG))
endef
endif

# sha passwords need USE_BB_CRYPT_SHA
ifeq ($(BR2_TARGET_GENERIC_PASSWD_SHA256)$(BR2_TARGET_GENERIC_PASSWD_SHA512),y)
define BUSYBOX_SET_CRYPT_SHA
	$(call KCONFIG_ENABLE_OPT,CONFIG_USE_BB_CRYPT_SHA,$(BUSYBOX_BUILD_CONFIG))
endef
endif

ifeq ($(BR2_USE_MMU),y)
define BUSYBOX_SET_MMU
	$(call KCONFIG_DISABLE_OPT,CONFIG_NOMMU,$(BUSYBOX_BUILD_CONFIG))
endef
else
define BUSYBOX_SET_MMU
	$(call KCONFIG_ENABLE_OPT,CONFIG_NOMMU,$(BUSYBOX_BUILD_CONFIG))
	$(call KCONFIG_DISABLE_OPT,CONFIG_SWAPON,$(BUSYBOX_BUILD_CONFIG))
	$(call KCONFIG_DISABLE_OPT,CONFIG_SWAPOFF,$(BUSYBOX_BUILD_CONFIG))
	$(call KCONFIG_DISABLE_OPT,CONFIG_ASH,$(BUSYBOX_BUILD_CONFIG))
	$(call KCONFIG_ENABLE_OPT,CONFIG_HUSH,$(BUSYBOX_BUILD_CONFIG))
	$(call KCONFIG_ENABLE_OPT,CONFIG_HUSH_BASH_COMPAT,$(BUSYBOX_BUILD_CONFIG))
	$(call KCONFIG_ENABLE_OPT,CONFIG_HUSH_BRACE_EXPANSION,$(BUSYBOX_BUILD_CONFIG))
	$(call KCONFIG_ENABLE_OPT,CONFIG_HUSH_HELP,$(BUSYBOX_BUILD_CONFIG))
	$(call KCONFIG_ENABLE_OPT,CONFIG_HUSH_INTERACTIVE,$(BUSYBOX_BUILD_CONFIG))
	$(call KCONFIG_ENABLE_OPT,CONFIG_HUSH_SAVEHISTORY,$(BUSYBOX_BUILD_CONFIG))
	$(call KCONFIG_ENABLE_OPT,CONFIG_HUSH_JOB,$(BUSYBOX_BUILD_CONFIG))
	$(call KCONFIG_ENABLE_OPT,CONFIG_HUSH_TICK,$(BUSYBOX_BUILD_CONFIG))
	$(call KCONFIG_ENABLE_OPT,CONFIG_HUSH_IF,$(BUSYBOX_BUILD_CONFIG))
	$(call KCONFIG_ENABLE_OPT,CONFIG_HUSH_LOOPS,$(BUSYBOX_BUILD_CONFIG))
	$(call KCONFIG_ENABLE_OPT,CONFIG_HUSH_CASE,$(BUSYBOX_BUILD_CONFIG))
	$(call KCONFIG_ENABLE_OPT,CONFIG_HUSH_FUNCTIONS,$(BUSYBOX_BUILD_CONFIG))
	$(call KCONFIG_ENABLE_OPT,CONFIG_HUSH_LOCAL,$(BUSYBOX_BUILD_CONFIG))
	$(call KCONFIG_ENABLE_OPT,CONFIG_HUSH_RANDOM_SUPPORT,$(BUSYBOX_BUILD_CONFIG))
	$(call KCONFIG_ENABLE_OPT,CONFIG_HUSH_EXPORT_N,$(BUSYBOX_BUILD_CONFIG))
	$(call KCONFIG_ENABLE_OPT,CONFIG_HUSH_MODE_X,$(BUSYBOX_BUILD_CONFIG))
endef
endif

# If we're using static libs do the same for busybox
ifeq ($(BR2_STATIC_LIBS),y)
define BUSYBOX_PREFER_STATIC
	$(call KCONFIG_ENABLE_OPT,CONFIG_STATIC,$(BUSYBOX_BUILD_CONFIG))
endef
endif

define BUSYBOX_INSTALL_UDHCPC_SCRIPT
	if grep -q CONFIG_UDHCPC=y $(@D)/.config; then \
		$(INSTALL) -m 0755 -D package/busybox/udhcpc.script \
			$(TARGET_DIR)/usr/share/udhcpc/default.script; \
		$(INSTALL) -m 0755 -d \
			$(TARGET_DIR)/usr/share/udhcpc/default.script.d; \
	fi
endef

ifeq ($(BR2_INIT_BUSYBOX),y)

define BUSYBOX_SET_INIT
	$(call KCONFIG_ENABLE_OPT,CONFIG_INIT,$(BUSYBOX_BUILD_CONFIG))
endef

ifeq ($(BR2_TARGET_GENERIC_GETTY),y)
define BUSYBOX_SET_GETTY
	$(SED) '/# GENERIC_SERIAL$$/s~^.*#~$(SYSTEM_GETTY_PORT)::respawn:/sbin/getty -L $(SYSTEM_GETTY_OPTIONS) $(SYSTEM_GETTY_PORT) $(SYSTEM_GETTY_BAUDRATE) $(SYSTEM_GETTY_TERM) #~' \
		$(TARGET_DIR)/etc/inittab
endef
BUSYBOX_TARGET_FINALIZE_HOOKS += BUSYBOX_SET_GETTY
endif # BR2_TARGET_GENERIC_GETTY

BUSYBOX_TARGET_FINALIZE_HOOKS += SYSTEM_REMOUNT_ROOT_INITTAB

endif # BR2_INIT_BUSYBOX

ifeq ($(BR2_PACKAGE_BUSYBOX_SELINUX),y)
BUSYBOX_DEPENDENCIES += host-pkgconf libselinux libsepol
define BUSYBOX_SET_SELINUX
	$(call KCONFIG_ENABLE_OPT,CONFIG_SELINUX,$(BUSYBOX_BUILD_CONFIG))
	$(call KCONFIG_ENABLE_OPT,CONFIG_SELINUXENABLED,$(BUSYBOX_BUILD_CONFIG))
endef
endif

ifeq ($(BR2_PACKAGE_BUSYBOX_INDIVIDUAL_BINARIES),y)
define BUSYBOX_SET_INDIVIDUAL_BINARIES
	$(call KCONFIG_ENABLE_OPT,CONFIG_BUILD_LIBBUSYBOX,$(BUSYBOX_BUILD_CONFIG))
	$(call KCONFIG_ENABLE_OPT,CONFIG_FEATURE_INDIVIDUAL,$(BUSYBOX_BUILD_CONFIG))
endef

define BUSYBOX_INSTALL_INDIVIDUAL_BINARIES
	rm -f $(TARGET_DIR)/bin/busybox
endef
endif

# Only install our logging scripts if no other package does it.
ifeq ($(BR2_PACKAGE_SYSKLOGD)$(BR2_PACKAGE_RSYSLOG)$(BR2_PACKAGE_SYSLOG_NG),)
define BUSYBOX_INSTALL_LOGGING_SCRIPT
	if grep -q CONFIG_SYSLOGD=y $(@D)/.config; \
	then \
		$(INSTALL) -m 0755 -D package/busybox/S01syslogd \
			$(TARGET_DIR)/etc/init.d/S01syslogd; \
	fi; \
	if grep -q CONFIG_KLOGD=y $(@D)/.config; \
	then \
		$(INSTALL) -m 0755 -D package/busybox/S02klogd \
			$(TARGET_DIR)/etc/init.d/S02klogd; \
	fi
endef
endif

# Only install our sysctl scripts if no other package does it.
ifeq ($(BR2_PACKAGE_PROCPS_NG),)
define BUSYBOX_INSTALL_SYSCTL_SCRIPT
	if grep -q CONFIG_BB_SYSCTL=y $(@D)/.config; \
	then \
		$(INSTALL) -m 0755 -D package/busybox/S02sysctl \
			$(TARGET_DIR)/etc/init.d/S02sysctl ; \
	fi
endef
endif

ifeq ($(BR2_INIT_BUSYBOX),y)
define BUSYBOX_INSTALL_INITTAB
	$(INSTALL) -D -m 0644 package/busybox/inittab $(TARGET_DIR)/etc/inittab
endef
endif

ifeq ($(BR2_PACKAGE_BUSYBOX_WATCHDOG),y)
define BUSYBOX_SET_WATCHDOG
	$(call KCONFIG_ENABLE_OPT,CONFIG_WATCHDOG,$(BUSYBOX_BUILD_CONFIG))
endef
define BUSYBOX_INSTALL_WATCHDOG_SCRIPT
	$(INSTALL) -D -m 0755 package/busybox/S15watchdog \
		$(TARGET_DIR)/etc/init.d/S15watchdog
	$(SED) s/PERIOD/$(call qstrip,$(BR2_PACKAGE_BUSYBOX_WATCHDOG_PERIOD))/ \
		$(TARGET_DIR)/etc/init.d/S15watchdog
endef
endif

# PAM support requires thread support in the toolchain
ifeq ($(BR2_PACKAGE_LINUX_PAM)$(BR2_TOOLCHAIN_HAS_THREADS),yy)
define BUSYBOX_LINUX_PAM
	$(call KCONFIG_ENABLE_OPT,CONFIG_PAM,$(BUSYBOX_BUILD_CONFIG))
endef
BUSYBOX_DEPENDENCIES += linux-pam
else
define BUSYBOX_LINUX_PAM
	$(call KCONFIG_DISABLE_OPT,CONFIG_PAM,$(BUSYBOX_BUILD_CONFIG))
endef
endif

# Telnet support
define BUSYBOX_INSTALL_TELNET_SCRIPT
	if grep -q CONFIG_FEATURE_TELNETD_STANDALONE=y $(@D)/.config; then \
		$(INSTALL) -m 0755 -D package/busybox/S50telnet \
			$(TARGET_DIR)/etc/init.d/S50telnet ; \
	fi
endef

# Add /bin/{a,hu}sh to /etc/shells otherwise some login tools like dropbear
# can reject the user connection. See man shells.
define BUSYBOX_INSTALL_ADD_TO_SHELLS
	if grep -q CONFIG_ASH=y $(@D)/.config; then \
		grep -qsE '^/bin/ash$$' $(TARGET_DIR)/etc/shells \
		|| echo "/bin/ash" >> $(TARGET_DIR)/etc/shells; \
	fi
	if grep -q CONFIG_HUSH=y $(@D)/.config; then \
		grep -qsE '^/bin/hush$$' $(TARGET_DIR)/etc/shells \
		|| echo "/bin/hush" >> $(TARGET_DIR)/etc/shells; \
	fi
endef
BUSYBOX_TARGET_FINALIZE_HOOKS += BUSYBOX_INSTALL_ADD_TO_SHELLS

define BUSYBOX_KCONFIG_FIXUP_CMDS
	$(BUSYBOX_SET_MMU)
	$(BUSYBOX_PREFER_STATIC)
	$(BUSYBOX_SET_MDEV)
	$(BUSYBOX_SET_CRYPT_SHA)
	$(BUSYBOX_LINUX_PAM)
	$(BUSYBOX_SET_INIT)
	$(BUSYBOX_SET_WATCHDOG)
	$(BUSYBOX_SET_SELINUX)
	$(BUSYBOX_SET_INDIVIDUAL_BINARIES)
endef

define BUSYBOX_BUILD_CMDS
	$(BUSYBOX_MAKE_ENV) $(MAKE) $(BUSYBOX_MAKE_OPTS) -C $(@D)
endef

define BUSYBOX_INSTALL_TARGET_CMDS
	# Use the 'noclobber' install rule, to prevent BusyBox from overwriting
	# any full-blown versions of apps installed by other packages.
	$(BUSYBOX_MAKE_ENV) $(MAKE) $(BUSYBOX_MAKE_OPTS) -C $(@D) install-noclobber
	$(BUSYBOX_INSTALL_INITTAB)
	$(BUSYBOX_INSTALL_UDHCPC_SCRIPT)
	$(BUSYBOX_INSTALL_MDEV_CONF)
endef

define BUSYBOX_INSTALL_INIT_SYSV
	$(BUSYBOX_INSTALL_MDEV_SCRIPT)
	$(BUSYBOX_INSTALL_LOGGING_SCRIPT)
	$(BUSYBOX_INSTALL_WATCHDOG_SCRIPT)
	$(BUSYBOX_INSTALL_SYSCTL_SCRIPT)
	$(BUSYBOX_INSTALL_TELNET_SCRIPT)
	$(BUSYBOX_INSTALL_INDIVIDUAL_BINARIES)
endef

# Checks to give errors that the user can understand
# Must be before we call to kconfig-package
ifeq ($(BR2_PACKAGE_BUSYBOX)$(BR_BUILDING),yy)
ifeq ($(call qstrip,$(BR2_PACKAGE_BUSYBOX_CONFIG)),)
$(error No BusyBox configuration file specified, check your BR2_PACKAGE_BUSYBOX_CONFIG setting)
endif
endif

$(eval $(kconfig-package))
