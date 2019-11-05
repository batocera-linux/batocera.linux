################################################################################
#
# policycoreutils
#
################################################################################

POLICYCOREUTILS_VERSION = 2.9
POLICYCOREUTILS_SITE = https://github.com/SELinuxProject/selinux/releases/download/20190315
POLICYCOREUTILS_LICENSE = GPL-2.0
POLICYCOREUTILS_LICENSE_FILES = COPYING

POLICYCOREUTILS_DEPENDENCIES = libsemanage libcap-ng

ifeq ($(BR2_PACKAGE_LINUX_PAM),y)
POLICYCOREUTILS_DEPENDENCIES += linux-pam
POLICYCOREUTILS_MAKE_OPTS += NAMESPACE_PRIV=y
define POLICYCOREUTILS_INSTALL_TARGET_LINUX_PAM_CONFS
	$(INSTALL) -D -m 0644 $(@D)/newrole/newrole-lspp.pamd $(TARGET_DIR)/etc/pam.d/newrole
	$(INSTALL) -D -m 0644 $(@D)/run_init/run_init.pamd $(TARGET_DIR)/etc/pam.d/run_init
endef
endif

ifeq ($(BR2_PACKAGE_AUDIT),y)
POLICYCOREUTILS_DEPENDENCIES += audit
POLICYCOREUTILS_MAKE_OPTS += AUDIT_LOG_PRIV=y
endif

# Enable LSPP_PRIV if both audit and linux pam are enabled
ifeq ($(BR2_PACKAGE_LINUX_PAM)$(BR2_PACKAGE_AUDIT),yy)
POLICYCOREUTILS_MAKE_OPTS += LSPP_PRIV=y
endif

# Undefining _FILE_OFFSET_BITS here because of a "bug" with glibc fts.h
# large file support.
# See https://bugzilla.redhat.com/show_bug.cgi?id=574992 for more information
POLICYCOREUTILS_MAKE_OPTS += \
	$(TARGET_CONFIGURE_OPTS) \
	CFLAGS="$(TARGET_CFLAGS) -U_FILE_OFFSET_BITS" \
	CPPFLAGS="$(TARGET_CPPFLAGS) -U_FILE_OFFSET_BITS"

POLICYCOREUTILS_MAKE_DIRS = \
	load_policy newrole run_init \
	secon semodule sestatus setfiles \
	setsebool

# We need to pass DESTDIR at build time because it's used by
# policycoreutils build system to find headers and libraries.
define POLICYCOREUTILS_BUILD_CMDS
	$(foreach d,$(POLICYCOREUTILS_MAKE_DIRS),
		$(MAKE) -C $(@D)/$(d) $(POLICYCOREUTILS_MAKE_OPTS) \
			DESTDIR=$(STAGING_DIR) all
	)
endef

define POLICYCOREUTILS_INSTALL_TARGET_CMDS
	$(foreach d,$(POLICYCOREUTILS_MAKE_DIRS),
		$(MAKE) -C $(@D)/$(d) $(POLICYCOREUTILS_MAKE_OPTS) \
			DESTDIR=$(TARGET_DIR) install
	)
endef

HOST_POLICYCOREUTILS_DEPENDENCIES = host-libsemanage

# Undefining _FILE_OFFSET_BITS here because of a "bug" with glibc fts.h
# large file support.
# See https://bugzilla.redhat.com/show_bug.cgi?id=574992 for more information
# We also need to pass PREFIX because it defaults to $(DESTDIR)/usr
HOST_POLICYCOREUTILS_MAKE_OPTS = \
	$(HOST_CONFIGURE_OPTS) \
	CFLAGS="$(HOST_CFLAGS) -U_FILE_OFFSET_BITS" \
	CPPFLAGS="$(HOST_CPPFLAGS) -U_FILE_OFFSET_BITS" \
	PREFIX=$(HOST_DIR) \
	ETCDIR=$(HOST_DIR)/etc \
	SBINDIR=$(HOST_DIR)/sbin

# Note: We are only building the programs required by the refpolicy build
HOST_POLICYCOREUTILS_MAKE_DIRS = \
	load_policy newrole run_init \
	secon semodule sestatus setfiles \
	setsebool

define HOST_POLICYCOREUTILS_BUILD_CMDS
	$(foreach d,$(HOST_POLICYCOREUTILS_MAKE_DIRS),
		$(MAKE) -C $(@D)/$(d) $(HOST_POLICYCOREUTILS_MAKE_OPTS) all
	)
endef

define HOST_POLICYCOREUTILS_INSTALL_CMDS
	$(foreach d,$(HOST_POLICYCOREUTILS_MAKE_DIRS),
		$(MAKE) -C $(@D)/$(d) $(HOST_POLICYCOREUTILS_MAKE_OPTS) install
	)
endef

$(eval $(generic-package))
$(eval $(host-generic-package))
