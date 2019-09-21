################################################################################
#
# skeleton-init-common
#
################################################################################

# The skeleton can't depend on the toolchain, since all packages depends on the
# skeleton and the toolchain is a target package, as is skeleton.
# Hence, skeleton would depends on the toolchain and the toolchain would depend
# on skeleton.
SKELETON_INIT_COMMON_ADD_TOOLCHAIN_DEPENDENCY = NO
SKELETON_INIT_COMMON_ADD_SKELETON_DEPENDENCY = NO

# The skeleton also handles the merged /usr case in the sysroot
SKELETON_INIT_COMMON_INSTALL_STAGING = YES

SKELETON_INIT_COMMON_PATH = system/skeleton

define SKELETON_INIT_COMMON_INSTALL_TARGET_CMDS
	$(call SYSTEM_RSYNC,$(SKELETON_INIT_COMMON_PATH),$(TARGET_DIR))
	$(call SYSTEM_USR_SYMLINKS_OR_DIRS,$(TARGET_DIR))
	$(call SYSTEM_LIB_SYMLINK,$(TARGET_DIR))
	$(SED) 's,@PATH@,$(BR2_SYSTEM_DEFAULT_PATH),' $(TARGET_DIR)/etc/profile
	$(INSTALL) -m 0644 support/misc/target-dir-warning.txt \
		$(TARGET_DIR_WARNING_FILE)
endef

# We don't care much about what goes in staging, as long as it is
# correctly setup for merged/non-merged /usr. The simplest is to
# fill it in with the content of the skeleton.
define SKELETON_INIT_COMMON_INSTALL_STAGING_CMDS
	$(call SYSTEM_RSYNC,$(SKELETON_INIT_COMMON_PATH),$(STAGING_DIR))
	$(call SYSTEM_USR_SYMLINKS_OR_DIRS,$(STAGING_DIR))
	$(call SYSTEM_LIB_SYMLINK,$(STAGING_DIR))
	$(INSTALL) -d -m 0755 $(STAGING_DIR)/usr/include
endef

SKELETON_INIT_COMMON_HOSTNAME = $(call qstrip,$(BR2_TARGET_GENERIC_HOSTNAME))
SKELETON_INIT_COMMON_ISSUE = $(call qstrip,$(BR2_TARGET_GENERIC_ISSUE))
SKELETON_INIT_COMMON_ROOT_PASSWD = $(call qstrip,$(BR2_TARGET_GENERIC_ROOT_PASSWD))
SKELETON_INIT_COMMON_PASSWD_METHOD = $(call qstrip,$(BR2_TARGET_GENERIC_PASSWD_METHOD))
SKELETON_INIT_COMMON_BIN_SH = $(call qstrip,$(BR2_SYSTEM_BIN_SH))

ifneq ($(SKELETON_INIT_COMMON_HOSTNAME),)
SKELETON_INIT_COMMON_HOSTS_LINE = $(SKELETON_INIT_COMMON_HOSTNAME)
SKELETON_INIT_COMMON_SHORT_HOSTNAME = $(firstword $(subst ., ,$(SKELETON_INIT_COMMON_HOSTNAME)))
ifneq ($(SKELETON_INIT_COMMON_HOSTNAME),$(SKELETON_INIT_COMMON_SHORT_HOSTNAME))
SKELETON_INIT_COMMON_HOSTS_LINE += $(SKELETON_INIT_COMMON_SHORT_HOSTNAME)
endif
define SKELETON_INIT_COMMON_SET_HOSTNAME
	mkdir -p $(TARGET_DIR)/etc
	echo "$(SKELETON_INIT_COMMON_HOSTNAME)" > $(TARGET_DIR)/etc/hostname
	$(SED) '$$a \127.0.1.1\t$(SKELETON_INIT_COMMON_HOSTS_LINE)' \
		-e '/^127.0.1.1/d' $(TARGET_DIR)/etc/hosts
endef
SKELETON_INIT_COMMON_TARGET_FINALIZE_HOOKS += SKELETON_INIT_COMMON_SET_HOSTNAME
endif

ifneq ($(SKELETON_INIT_COMMON_ISSUE),)
define SKELETON_INIT_COMMON_SET_ISSUE
	mkdir -p $(TARGET_DIR)/etc
	echo "$(SKELETON_INIT_COMMON_ISSUE)" > $(TARGET_DIR)/etc/issue
endef
SKELETON_INIT_COMMON_TARGET_FINALIZE_HOOKS += SKELETON_INIT_COMMON_SET_ISSUE
endif

ifeq ($(BR2_TARGET_ENABLE_ROOT_LOGIN),y)
ifneq ($(filter $$1$$% $$5$$% $$6$$%,$(SKELETON_INIT_COMMON_ROOT_PASSWD)),)
SKELETON_INIT_COMMON_ROOT_PASSWORD = '$(SKELETON_INIT_COMMON_ROOT_PASSWD)'
else ifneq ($(SKELETON_INIT_COMMON_ROOT_PASSWD),)
# This variable will only be evaluated in the finalize stage, so we can
# be sure that host-mkpasswd will have already been built by that time.
SKELETON_INIT_COMMON_ROOT_PASSWORD = "`$(MKPASSWD) -m "$(SKELETON_INIT_COMMON_PASSWD_METHOD)" "$(SKELETON_INIT_COMMON_ROOT_PASSWD)"`"
endif
else # !BR2_TARGET_ENABLE_ROOT_LOGIN
SKELETON_INIT_COMMON_ROOT_PASSWORD = "*"
endif
# batocera
#define SKELETON_INIT_COMMON_SET_ROOT_PASSWD
#	$(SED) s,^root:[^:]*:,root:$(SKELETON_INIT_COMMON_ROOT_PASSWORD):, $(TARGET_DIR)/etc/shadow
#endef
#SKELETON_INIT_COMMON_TARGET_FINALIZE_HOOKS += SKELETON_INIT_COMMON_SET_ROOT_PASSWD

ifeq ($(BR2_SYSTEM_BIN_SH_NONE),y)
define SKELETON_INIT_COMMON_SET_BIN_SH
	rm -f $(TARGET_DIR)/bin/sh
endef
else
# Add /bin/sh to /etc/shells otherwise some login tools like dropbear
# can reject the user connection. See man shells.
define SKELETON_INIT_COMMON_ADD_SH_TO_SHELLS
	grep -qsE '^/bin/sh$$' $(TARGET_DIR)/etc/shells \
		|| echo "/bin/sh" >> $(TARGET_DIR)/etc/shells
endef
SKELETON_INIT_COMMON_TARGET_FINALIZE_HOOKS += SKELETON_INIT_COMMON_ADD_SH_TO_SHELLS
ifneq ($(SKELETON_INIT_COMMON_BIN_SH),)
define SKELETON_INIT_COMMON_SET_BIN_SH
	ln -sf $(SKELETON_INIT_COMMON_BIN_SH) $(TARGET_DIR)/bin/sh
	$(SED) '/^root:/s,[^/]*$$,$(SKELETON_INIT_COMMON_BIN_SH),' \
		$(TARGET_DIR)/etc/passwd
endef
endif
endif
SKELETON_INIT_COMMON_TARGET_FINALIZE_HOOKS += SKELETON_INIT_COMMON_SET_BIN_SH

$(eval $(generic-package))
