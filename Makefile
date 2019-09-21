# Makefile for buildroot
#
# Copyright (C) 1999-2005 by Erik Andersen <andersen@codepoet.org>
# Copyright (C) 2006-2014 by the Buildroot developers <buildroot@uclibc.org>
# Copyright (C) 2014-2019 by the Buildroot developers <buildroot@buildroot.org>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
#

#--------------------------------------------------------------
# Just run 'make menuconfig', configure stuff, then run 'make'.
# You shouldn't need to mess with anything beyond this point...
#--------------------------------------------------------------

# Delete default rules. We don't use them. This saves a bit of time.
.SUFFIXES:

# we want bash as shell
SHELL := $(shell if [ -x "$$BASH" ]; then echo $$BASH; \
	 else if [ -x /bin/bash ]; then echo /bin/bash; \
	 else echo sh; fi; fi)

# Set O variable if not already done on the command line;
# or avoid confusing packages that can use the O=<dir> syntax for out-of-tree
# build by preventing it from being forwarded to sub-make calls.
ifneq ("$(origin O)", "command line")
O := $(CURDIR)/output
endif

# Check if the current Buildroot execution meets all the pre-requisites.
# If they are not met, Buildroot will actually do its job in a sub-make meeting
# its pre-requisites, which are:
#  1- Permissive enough umask:
#       Wrong or too restrictive umask will prevent Buildroot and packages from
#       creating files and directories.
#  2- Absolute canonical CWD (i.e. $(CURDIR)):
#       Otherwise, some packages will use CWD as-is, others will compute its
#       absolute canonical path. This makes harder tracking and fixing host
#       machine path leaks.
#  3- Absolute canonical output location (i.e. $(O)):
#       For the same reason as the one for CWD.

# Remove the trailing '/.' from $(O) as it can be added by the makefile wrapper
# installed in the $(O) directory.
# Also remove the trailing '/' the user can set when on the command line.
override O := $(patsubst %/,%,$(patsubst %.,%,$(O)))
# Make sure $(O) actually exists before calling realpath on it; this is to
# avoid empty CANONICAL_O in case on non-existing entry.
CANONICAL_O := $(shell mkdir -p $(O) >/dev/null 2>&1)$(realpath $(O))

# gcc fails to build when the srcdir contains a '@'
ifneq ($(findstring @,$(CANONICAL_O)),)
$(error The build directory can not contain a '@')
endif

CANONICAL_CURDIR = $(realpath $(CURDIR))

REQ_UMASK = 0022

# Make sure O= is passed (with its absolute canonical path) everywhere the
# toplevel makefile is called back.
EXTRAMAKEARGS := O=$(CANONICAL_O)

# Check Buildroot execution pre-requisites here.
ifneq ($(shell umask):$(CURDIR):$(O),$(REQ_UMASK):$(CANONICAL_CURDIR):$(CANONICAL_O))
.PHONY: _all $(MAKECMDGOALS)

$(MAKECMDGOALS): _all
	@:

_all:
	@umask $(REQ_UMASK) && \
		$(MAKE) -C $(CANONICAL_CURDIR) --no-print-directory \
			$(MAKECMDGOALS) $(EXTRAMAKEARGS)

else # umask / $(CURDIR) / $(O)

# This is our default rule, so must come first
all:
.PHONY: all

# Set and export the version string
export BR2_VERSION := 2019.08-rc3
# Actual time the release is cut (for reproducible builds)
BR2_VERSION_EPOCH = 1567026000

# Save running make version since it's clobbered by the make package
RUNNING_MAKE_VERSION := $(MAKE_VERSION)

# Check for minimal make version (note: this check will break at make 10.x)
MIN_MAKE_VERSION = 3.81
ifneq ($(firstword $(sort $(RUNNING_MAKE_VERSION) $(MIN_MAKE_VERSION))),$(MIN_MAKE_VERSION))
$(error You have make '$(RUNNING_MAKE_VERSION)' installed. GNU make >= $(MIN_MAKE_VERSION) is required)
endif

# absolute path
TOPDIR := $(CURDIR)
CONFIG_CONFIG_IN = Config.in
CONFIG = support/kconfig
DATE := $(shell date +%Y%m%d)

# Compute the full local version string so packages can use it as-is
# Need to export it, so it can be got from environment in children (eg. mconf)
export BR2_VERSION_FULL := $(BR2_VERSION)$(shell $(TOPDIR)/support/scripts/setlocalversion)

# List of targets and target patterns for which .config doesn't need to be read in
noconfig_targets := menuconfig nconfig gconfig xconfig config oldconfig randconfig \
	defconfig %_defconfig allyesconfig allnoconfig alldefconfig syncconfig release \
	randpackageconfig allyespackageconfig allnopackageconfig \
	print-version olddefconfig distclean manual manual-% check-package

# Some global targets do not trigger a build, but are used to collect
# metadata, or do various checks. When such targets are triggered,
# some packages should not do their configuration sanity
# checks. Provide them a BR_BUILDING variable set to 'y' when we're
# actually building and they should do their sanity checks.
#
# We're building in two situations: when MAKECMDGOALS is empty
# (default target is to build), or when MAKECMDGOALS contains
# something else than one of the nobuild_targets.
nobuild_targets := source %-source \
	legal-info %-legal-info external-deps _external-deps \
	clean distclean help show-targets graph-depends \
	%-graph-depends %-show-depends %-show-version \
	graph-build graph-size list-defconfigs \
	savedefconfig update-defconfig printvars
ifeq ($(MAKECMDGOALS),)
BR_BUILDING = y
else ifneq ($(filter-out $(nobuild_targets),$(MAKECMDGOALS)),)
BR_BUILDING = y
endif

# We call make recursively to build packages. The command-line overrides that
# are passed to Buildroot don't apply to those package build systems. In
# particular, we don't want to pass down the O=<dir> option for out-of-tree
# builds, because the value specified on the command line will not be correct
# for packages.
MAKEOVERRIDES :=

# Include some helper macros and variables
include support/misc/utils.mk

# Set variables related to in-tree or out-of-tree build.
# Here, both $(O) and $(CURDIR) are absolute canonical paths.
ifeq ($(O),$(CURDIR)/output)
CONFIG_DIR := $(CURDIR)
NEED_WRAPPER =
else
CONFIG_DIR := $(O)
NEED_WRAPPER = y
endif

# bash prints the name of the directory on 'cd <dir>' if CDPATH is
# set, so unset it here to not cause problems. Notice that the export
# line doesn't affect the environment of $(shell ..) calls.
export CDPATH :=

BASE_DIR := $(CANONICAL_O)
$(if $(BASE_DIR),, $(error output directory "$(O)" does not exist))


# Handling of BR2_EXTERNAL.
#
# The value of BR2_EXTERNAL is stored in .br-external in the output directory.
# The location of the external.mk makefile fragments is computed in that file.
# On subsequent invocations of make, this file is read in. BR2_EXTERNAL can
# still be overridden on the command line, therefore the file is re-created
# every time make is run.

BR2_EXTERNAL_FILE = $(BASE_DIR)/.br2-external.mk
-include $(BR2_EXTERNAL_FILE)
$(shell support/scripts/br2-external -d '$(BASE_DIR)' $(BR2_EXTERNAL))
BR2_EXTERNAL_ERROR =
include $(BR2_EXTERNAL_FILE)
ifneq ($(BR2_EXTERNAL_ERROR),)
$(error $(BR2_EXTERNAL_ERROR))
endif

# To make sure that the environment variable overrides the .config option,
# set this before including .config.
ifneq ($(BR2_DL_DIR),)
DL_DIR := $(BR2_DL_DIR)
endif
ifneq ($(BR2_CCACHE_DIR),)
BR_CACHE_DIR := $(BR2_CCACHE_DIR)
endif

# Need that early, before we scan packages
# Avoids doing the $(or...) everytime
BR_GRAPH_OUT := $(or $(BR2_GRAPH_OUT),pdf)

BUILD_DIR := $(BASE_DIR)/build
BINARIES_DIR := $(BASE_DIR)/images
BASE_TARGET_DIR := $(BASE_DIR)/target
# initial definition so that 'make clean' works for most users, even without
# .config. HOST_DIR will be overwritten later when .config is included.
HOST_DIR := $(BASE_DIR)/host
GRAPHS_DIR := $(BASE_DIR)/graphs

LEGAL_INFO_DIR = $(BASE_DIR)/legal-info
REDIST_SOURCES_DIR_TARGET = $(LEGAL_INFO_DIR)/sources
REDIST_SOURCES_DIR_HOST = $(LEGAL_INFO_DIR)/host-sources
LICENSE_FILES_DIR_TARGET = $(LEGAL_INFO_DIR)/licenses
LICENSE_FILES_DIR_HOST = $(LEGAL_INFO_DIR)/host-licenses
LEGAL_MANIFEST_CSV_TARGET = $(LEGAL_INFO_DIR)/manifest.csv
LEGAL_MANIFEST_CSV_HOST = $(LEGAL_INFO_DIR)/host-manifest.csv
LEGAL_WARNINGS = $(LEGAL_INFO_DIR)/.warnings
LEGAL_REPORT = $(LEGAL_INFO_DIR)/README

BR2_CONFIG = $(CONFIG_DIR)/.config

# Pull in the user's configuration file
ifeq ($(filter $(noconfig_targets),$(MAKECMDGOALS)),)
-include $(BR2_CONFIG)
endif

# Parallel execution of this Makefile is disabled because it changes
# the packages building order, that can be a problem for two reasons:
# - If a package has an unspecified optional dependency and that
#   dependency is present when the package is built, it is used,
#   otherwise it isn't (but compilation happily proceeds) so the end
#   result will differ if the order is swapped due to parallel
#   building.
# - Also changing the building order can be a problem if two packages
#   manipulate the same file in the target directory.
#
# Taking into account the above considerations, if you still want to execute
# this top-level Makefile in parallel comment the ".NOTPARALLEL" line and
# use the -j<jobs> option when building, e.g:
#      make -j$((`getconf _NPROCESSORS_ONLN`+1))
.NOTPARALLEL:

# timezone and locale may affect build output
ifeq ($(BR2_REPRODUCIBLE),y)
export TZ = UTC
export LANG = C
export LC_ALL = C
endif

# To put more focus on warnings, be less verbose as default
# Use 'make V=1' to see the full commands
ifeq ("$(origin V)", "command line")
  KBUILD_VERBOSE = $(V)
endif
ifndef KBUILD_VERBOSE
  KBUILD_VERBOSE = 0
endif

ifeq ($(KBUILD_VERBOSE),1)
  Q =
ifndef VERBOSE
  VERBOSE = 1
endif
export VERBOSE
else
  Q = @
endif

# kconfig uses CONFIG_SHELL
CONFIG_SHELL := $(SHELL)

export SHELL CONFIG_SHELL Q KBUILD_VERBOSE

ifndef HOSTAR
HOSTAR := ar
endif
ifndef HOSTAS
HOSTAS := as
endif
ifndef HOSTCC
HOSTCC := gcc
HOSTCC := $(shell which $(HOSTCC) || type -p $(HOSTCC) || echo gcc)
endif
HOSTCC_NOCCACHE := $(HOSTCC)
ifndef HOSTCXX
HOSTCXX := g++
HOSTCXX := $(shell which $(HOSTCXX) || type -p $(HOSTCXX) || echo g++)
endif
HOSTCXX_NOCCACHE := $(HOSTCXX)
ifndef HOSTCPP
HOSTCPP := cpp
endif
ifndef HOSTLD
HOSTLD := ld
endif
ifndef HOSTLN
HOSTLN := ln
endif
ifndef HOSTNM
HOSTNM := nm
endif
ifndef HOSTOBJCOPY
HOSTOBJCOPY := objcopy
endif
ifndef HOSTRANLIB
HOSTRANLIB := ranlib
endif
HOSTAR := $(shell which $(HOSTAR) || type -p $(HOSTAR) || echo ar)
HOSTAS := $(shell which $(HOSTAS) || type -p $(HOSTAS) || echo as)
HOSTCPP := $(shell which $(HOSTCPP) || type -p $(HOSTCPP) || echo cpp)
HOSTLD := $(shell which $(HOSTLD) || type -p $(HOSTLD) || echo ld)
HOSTLN := $(shell which $(HOSTLN) || type -p $(HOSTLN) || echo ln)
HOSTNM := $(shell which $(HOSTNM) || type -p $(HOSTNM) || echo nm)
HOSTOBJCOPY := $(shell which $(HOSTOBJCOPY) || type -p $(HOSTOBJCOPY) || echo objcopy)
HOSTRANLIB := $(shell which $(HOSTRANLIB) || type -p $(HOSTRANLIB) || echo ranlib)
SED := $(shell which sed || type -p sed) -i -e

export HOSTAR HOSTAS HOSTCC HOSTCXX HOSTLD
export HOSTCC_NOCCACHE HOSTCXX_NOCCACHE

# Determine the userland we are running on.
#
# Note that, despite its name, we are not interested in the actual
# architecture name. This is mostly used to determine whether some
# of the binary tools (e.g. pre-built external toolchains) can run
# on the current host. So we need to know if the userland we're
# running on can actually run those toolchains.
#
# For example, a 64-bit prebuilt toolchain will not run on a 64-bit
# kernel if the userland is 32-bit (e.g. in a chroot for example).
#
# So, we extract the first part of the tuple the host gcc was
# configured to generate code for; we assume this is our userland.
#
export HOSTARCH := $(shell LC_ALL=C $(HOSTCC_NOCCACHE) -v 2>&1 | \
	sed -e '/^Target: \([^-]*\).*/!d' \
	    -e 's//\1/' \
	    -e 's/i.86/x86/' \
	    -e 's/sun4u/sparc64/' \
	    -e 's/arm.*/arm/' \
	    -e 's/sa110/arm/' \
	    -e 's/ppc64/powerpc64/' \
	    -e 's/ppc/powerpc/' \
	    -e 's/macppc/powerpc/' \
	    -e 's/sh.*/sh/' )

# When adding a new host gcc version in Config.in,
# update the HOSTCC_MAX_VERSION variable:
HOSTCC_MAX_VERSION := 8

HOSTCC_VERSION := $(shell V=$$($(HOSTCC_NOCCACHE) --version | \
	sed -n -r 's/^.* ([0-9]*)\.([0-9]*)\.([0-9]*)[ ]*.*/\1 \2/p'); \
	[ "$${V%% *}" -le $(HOSTCC_MAX_VERSION) ] || V=$(HOSTCC_MAX_VERSION); \
	printf "%s" "$${V}")

# For gcc >= 5.x, we only need the major version.
ifneq ($(firstword $(HOSTCC_VERSION)),4)
HOSTCC_VERSION := $(firstword $(HOSTCC_VERSION))
endif

ifeq ($(BR2_NEEDS_HOST_UTF8_LOCALE),y)
# First, we try to use the user's configured locale (as that's the
# language they'd expect messages to be displayed), then we favour
# a non language-specific locale like C.UTF-8 if one is available,
# so we sort with the C locale to get it at the top.
# This is guaranteed to not be empty, because of the check in
# support/dependencies/dependencies.sh
HOST_UTF8_LOCALE := $(shell \
			( echo $${LC_ALL:-$${LC_MESSAGES:-$${LANG}}}; \
			  locale -a 2>/dev/null | LC_ALL=C sort \
			) \
			| grep -i -E 'utf-?8$$' \
			| head -n 1)
HOST_UTF8_LOCALE_ENV := LC_ALL=$(HOST_UTF8_LOCALE)
endif

# Make sure pkg-config doesn't look outside the buildroot tree
HOST_PKG_CONFIG_PATH := $(PKG_CONFIG_PATH)
unexport PKG_CONFIG_PATH
unexport PKG_CONFIG_SYSROOT_DIR
unexport PKG_CONFIG_LIBDIR

# Having DESTDIR set in the environment confuses the installation
# steps of some packages.
unexport DESTDIR

# Causes breakage with packages that needs host-ruby
unexport RUBYOPT

include package/pkg-utils.mk
include package/doc-asciidoc.mk

ifeq ($(BR2_HAVE_DOT_CONFIG),y)

################################################################################
#
# Hide troublesome environment variables from sub processes
#
################################################################################
unexport CROSS_COMPILE
unexport ARCH
unexport CC
unexport LD
unexport AR
unexport CXX
unexport CPP
unexport RANLIB
unexport CFLAGS
unexport CXXFLAGS
unexport GREP_OPTIONS
unexport TAR_OPTIONS
unexport CONFIG_SITE
unexport QMAKESPEC
unexport TERMINFO
unexport MACHINE
unexport O
unexport GCC_COLORS
unexport PLATFORM
unexport OS

GNU_HOST_NAME := $(shell support/gnuconfig/config.guess)

PACKAGES :=
PACKAGES_ALL :=

# silent mode requested?
QUIET := $(if $(findstring s,$(filter-out --%,$(MAKEFLAGS))),-q)

# Strip off the annoying quoting
ARCH := $(call qstrip,$(BR2_ARCH))

KERNEL_ARCH := $(shell echo "$(ARCH)" | sed -e "s/-.*//" \
	-e s/i.86/i386/ -e s/sun4u/sparc64/ \
	-e s/arcle/arc/ \
	-e s/arceb/arc/ \
	-e s/arm.*/arm/ -e s/sa110/arm/ \
	-e s/aarch64.*/arm64/ \
	-e s/nds32.*/nds32/ \
	-e s/or1k/openrisc/ \
	-e s/parisc64/parisc/ \
	-e s/powerpc64.*/powerpc/ \
	-e s/ppc.*/powerpc/ -e s/mips.*/mips/ \
	-e s/riscv.*/riscv/ \
	-e s/sh.*/sh/ \
	-e s/microblazeel/microblaze/)

ZCAT := $(call qstrip,$(BR2_ZCAT))
BZCAT := $(call qstrip,$(BR2_BZCAT))
XZCAT := $(call qstrip,$(BR2_XZCAT))
LZCAT := $(call qstrip,$(BR2_LZCAT))
TAR_OPTIONS = $(call qstrip,$(BR2_TAR_OPTIONS)) -xf

# packages compiled for the host go here
HOST_DIR := $(call qstrip,$(BR2_HOST_DIR))

# The target directory is common to all packages,
# but there is one that is specific to each filesystem.
TARGET_DIR = $(if $(ROOTFS),$(ROOTFS_$(ROOTFS)_TARGET_DIR),$(BASE_TARGET_DIR))

ifneq ($(HOST_DIR),$(BASE_DIR)/host)
HOST_DIR_SYMLINK = $(BASE_DIR)/host
$(HOST_DIR_SYMLINK): $(BASE_DIR)
	ln -snf $(HOST_DIR) $(BASE_DIR)/host
endif

# Quotes are needed for spaces and all in the original PATH content.
BR_PATH = "$(HOST_DIR)/bin:$(HOST_DIR)/sbin:$(PATH)"

# Location of a file giving a big fat warning that output/target
# should not be used as the root filesystem.
TARGET_DIR_WARNING_FILE = $(TARGET_DIR)/THIS_IS_NOT_YOUR_ROOT_FILESYSTEM

ifeq ($(BR2_CCACHE),y)
CCACHE = $(HOST_DIR)/bin/ccache
BR_CACHE_DIR ?= $(call qstrip,$(BR2_CCACHE_DIR))
export BR_CACHE_DIR
HOSTCC = $(CCACHE) $(HOSTCC_NOCCACHE)
HOSTCXX = $(CCACHE) $(HOSTCXX_NOCCACHE)
else
export BR_NO_CCACHE
endif

# Scripts in support/ or post-build scripts may need to reference
# these locations, so export them so it is easier to use
export BR2_CONFIG
export BR2_REPRODUCIBLE
export TARGET_DIR
export STAGING_DIR
export HOST_DIR
export BINARIES_DIR
export BASE_DIR

################################################################################
#
# You should probably leave this stuff alone unless you know
# what you are doing.
#
################################################################################

all: world

# Include legacy before the other things, because package .mk files
# may rely on it.
include Makefile.legacy

include system/system.mk
include package/Makefile.in
# arch/arch.mk must be after package/Makefile.in because it may need to
# complement variables defined therein, like BR_NO_CHECK_HASH_FOR.
include arch/arch.mk
include support/dependencies/dependencies.mk

include $(sort $(wildcard toolchain/*.mk))
include $(sort $(wildcard toolchain/*/*.mk))

ifeq ($(BR2_REPRODUCIBLE),y)
# If SOURCE_DATE_EPOCH has not been set then use the commit date, or the last
# release date if the source tree is not within a Git repository.
# See: https://reproducible-builds.org/specs/source-date-epoch/
BR2_VERSION_GIT_EPOCH := $(shell $(GIT) log -1 --format=%at 2> /dev/null)
export SOURCE_DATE_EPOCH ?= $(or $(BR2_VERSION_GIT_EPOCH),$(BR2_VERSION_EPOCH))
endif

# Include the package override file if one has been provided in the
# configuration.
PACKAGE_OVERRIDE_FILE = $(call qstrip,$(BR2_PACKAGE_OVERRIDE_FILE))
ifneq ($(PACKAGE_OVERRIDE_FILE),)
-include $(PACKAGE_OVERRIDE_FILE)
endif

include $(sort $(wildcard package/*/*.mk))

include boot/common.mk
include linux/linux.mk
include fs/common.mk

# If using a br2-external tree, the BR2_EXTERNAL_$(NAME)_PATH variables
# are also present in the .config file. Since .config is included after
# we defined them in the Makefile, the values for those variables are
# quoted. We just include the generated Makefile fragment .br2-external.mk
# a third time, which will set those variables to the un-quoted values.
include $(BR2_EXTERNAL_FILE)

# Nothing to include if no BR2_EXTERNAL tree in use
include $(BR2_EXTERNAL_MKS)

# Now we are sure we have all the packages scanned and defined. We now
# check for each package in the list of enabled packages, that all its
# dependencies are indeed enabled.
#
# Only trigger the check for default builds. If the user forces building
# a package, even if not enabled in the configuration, we want to accept
# it. However; we also want to be able to force checking the dependencies
# if the user so desires. Forcing a dependency check is useful in the case
# of test-pkg, as we want to make sure during testing, that a package has
# all the dependencies selected in the config file.
#
ifeq ($(MAKECMDGOALS),)
BR_FORCE_CHECK_DEPENDENCIES = YES
endif

ifeq ($(BR_FORCE_CHECK_DEPENDENCIES),YES)

define CHECK_ONE_DEPENDENCY
ifeq ($$($(2)_TYPE),target)
ifeq ($$($(2)_IS_VIRTUAL),)
ifneq ($$($$($(2)_KCONFIG_VAR)),y)
$$(error $$($(2)_NAME) is in the dependency chain of $$($(1)_NAME) that \
has added it to its _DEPENDENCIES variable without selecting it or \
depending on it from Config.in)
endif
endif
endif
endef

$(foreach pkg,$(call UPPERCASE,$(PACKAGES)),\
	$(foreach dep,$(call UPPERCASE,$($(pkg)_FINAL_ALL_DEPENDENCIES)),\
		$(eval $(call CHECK_ONE_DEPENDENCY,$(pkg),$(dep))$(sep))))

endif

$(BUILD_DIR)/buildroot-config/auto.conf: $(BR2_CONFIG)
	$(MAKE1) $(EXTRAMAKEARGS) HOSTCC="$(HOSTCC_NOCCACHE)" HOSTCXX="$(HOSTCXX_NOCCACHE)" syncconfig

.PHONY: prepare
prepare: $(BUILD_DIR)/buildroot-config/auto.conf

.PHONY: world
world: target-post-image

.PHONY: prepare-sdk
prepare-sdk: world
	@$(call MESSAGE,"Rendering the SDK relocatable")
	$(TOPDIR)/support/scripts/fix-rpath host
	$(TOPDIR)/support/scripts/fix-rpath staging
	$(INSTALL) -m 755 $(TOPDIR)/support/misc/relocate-sdk.sh $(HOST_DIR)/relocate-sdk.sh
	mkdir -p $(HOST_DIR)/share/buildroot
	echo $(HOST_DIR) > $(HOST_DIR)/share/buildroot/sdk-location

BR2_SDK_PREFIX ?= $(GNU_TARGET_NAME)_sdk-buildroot
.PHONY: sdk
sdk: prepare-sdk $(BR2_TAR_HOST_DEPENDENCY)
	@$(call MESSAGE,"Generating SDK tarball")
	$(if $(BR2_SDK_PREFIX),,$(error BR2_SDK_PREFIX can not be empty))
	$(Q)mkdir -p $(BINARIES_DIR)
	$(TAR) czf "$(BINARIES_DIR)/$(BR2_SDK_PREFIX).tar.gz" \
		--owner=0 --group=0 --numeric-owner \
		--transform='s#^$(patsubst /%,%,$(HOST_DIR))#$(BR2_SDK_PREFIX)#' \
		-C / $(patsubst /%,%,$(HOST_DIR))

RSYNC_VCS_EXCLUSIONS = \
	--exclude .svn --exclude .git --exclude .hg --exclude .bzr \
	--exclude CVS

# When stripping, obey to BR2_STRIP_EXCLUDE_DIRS and
# BR2_STRIP_EXCLUDE_FILES
STRIP_FIND_COMMON_CMD = \
	find $(TARGET_DIR) \
	$(if $(call qstrip,$(BR2_STRIP_EXCLUDE_DIRS)), \
		\( $(call finddirclauses,$(TARGET_DIR),$(call qstrip,$(BR2_STRIP_EXCLUDE_DIRS))) \) \
		-prune -o \
	) \
	$(if $(call qstrip,$(BR2_STRIP_EXCLUDE_FILES)), \
		-not \( $(call findfileclauses,$(call qstrip,$(BR2_STRIP_EXCLUDE_FILES))) \) )

# Regular stripping for everything, except libpthread, ld-*.so and
# kernel modules:
# - libpthread.so: a non-stripped libpthread shared library is needed for
#   proper debugging of pthread programs using gdb.
# - ld.so: a non-stripped dynamic linker library is needed for valgrind
# - kernel modules (*.ko): do not function properly when stripped like normal
#   applications and libraries. Normally kernel modules are already excluded
#   by the executable permission check, so the explicit exclusion is only
#   done for kernel modules with incorrect permissions.
STRIP_FIND_CMD = \
	$(STRIP_FIND_COMMON_CMD) \
	-type f \( -perm /111 -o -name '*.so*' \) \
	-not \( $(call findfileclauses,libpthread*.so* ld-*.so* *.ko) \) \
	-print0

# Special stripping (only debugging symbols) for libpthread and ld-*.so.
STRIP_FIND_SPECIAL_LIBS_CMD = \
	$(STRIP_FIND_COMMON_CMD) \
	\( -name 'ld-*.so*' -o -name 'libpthread*.so*' \) \
	-print0

ifeq ($(BR2_ECLIPSE_REGISTER),y)
define TOOLCHAIN_ECLIPSE_REGISTER
	./support/scripts/eclipse-register-toolchain `readlink -f $(O)` \
		$(notdir $(TARGET_CROSS)) $(BR2_ARCH)
endef
TARGET_FINALIZE_HOOKS += TOOLCHAIN_ECLIPSE_REGISTER
endif

# Generate locale data. Basically, we call the localedef program
# (built by the host-localedef package) for each locale. The input
# data comes preferably from the toolchain, or if the toolchain does
# not have them (Linaro toolchains), we use the ones available on the
# host machine.
ifeq ($(BR2_TOOLCHAIN_USES_GLIBC),y)
GLIBC_GENERATE_LOCALES = $(call qstrip,$(BR2_GENERATE_LOCALE))
ifneq ($(GLIBC_GENERATE_LOCALES),)
PACKAGES += host-localedef

define GENERATE_GLIBC_LOCALES
	$(Q)mkdir -p $(TARGET_DIR)/usr/lib/locale/
	$(Q)for locale in $(GLIBC_GENERATE_LOCALES) ; do \
		inputfile=`echo $${locale} | cut -f1 -d'.'` ; \
		charmap=`echo $${locale} | cut -f2 -d'.' -s` ; \
		if test -z "$${charmap}" ; then \
			charmap="UTF-8" ; \
		fi ; \
		echo "Generating locale $${inputfile}.$${charmap}" ; \
		I18NPATH=$(STAGING_DIR)/usr/share/i18n:/usr/share/i18n \
		$(HOST_DIR)/bin/localedef \
			--prefix=$(TARGET_DIR) \
			--$(call LOWERCASE,$(BR2_ENDIAN))-endian \
			-i $${inputfile} -f $${charmap} \
			$${locale} ; \
	done
endef
TARGET_FINALIZE_HOOKS += GENERATE_GLIBC_LOCALES
endif
endif

ifeq ($(BR2_ENABLE_LOCALE_PURGE),y)
LOCALE_WHITELIST = $(BUILD_DIR)/locales.nopurge
LOCALE_NOPURGE = $(call qstrip,$(BR2_ENABLE_LOCALE_WHITELIST))

# This piece of junk does the following:
# First collect the whitelist in a file.
# Then go over all the locale dirs and for each subdir, check if it exists
# in the whitelist file. If it doesn't, kill it.
# Finally, specifically for X11, regenerate locale.dir from the whitelist.
define PURGE_LOCALES
	rm -f $(LOCALE_WHITELIST)
	for i in $(LOCALE_NOPURGE) locale-archive; do echo $$i >> $(LOCALE_WHITELIST); done

	for dir in $(wildcard $(addprefix $(TARGET_DIR),/usr/share/locale /usr/share/X11/locale /usr/lib/locale)); \
	do \
		for langdir in $$dir/*; \
		do \
			if [ -e "$${langdir}" ]; \
			then \
				grep -qx "$${langdir##*/}" $(LOCALE_WHITELIST) || rm -rf $$langdir; \
			fi \
		done; \
	done
	if [ -d $(TARGET_DIR)/usr/share/X11/locale ]; \
	then \
		for lang in $(LOCALE_NOPURGE); \
		do \
			if [ -f $(TARGET_DIR)/usr/share/X11/locale/$$lang/XLC_LOCALE ]; \
			then \
				echo "$$lang/XLC_LOCALE: $$lang"; \
			fi \
		done > $(TARGET_DIR)/usr/share/X11/locale/locale.dir; \
	fi
endef
TARGET_FINALIZE_HOOKS += PURGE_LOCALES
endif

$(TARGETS_ROOTFS): target-finalize

# Avoid the rootfs name leaking down the dependency chain
target-finalize: ROOTFS=

host-finalize: $(HOST_DIR_SYMLINK)

.PHONY: staging-finalize
staging-finalize:
	@ln -snf $(STAGING_DIR) $(BASE_DIR)/staging

.PHONY: target-finalize
target-finalize: $(PACKAGES) host-finalize
	@$(call MESSAGE,"Finalizing target directory")
	# Check files that are touched by more than one package
	# batocera
	#./support/scripts/check-uniq-files -t target $(BUILD_DIR)/packages-file-list.txt
	#./support/scripts/check-uniq-files -t staging $(BUILD_DIR)/packages-file-list-staging.txt
	#./support/scripts/check-uniq-files -t host $(BUILD_DIR)/packages-file-list-host.txt
	$(foreach hook,$(TARGET_FINALIZE_HOOKS),$($(hook))$(sep))
	rm -rf $(TARGET_DIR)/usr/include $(TARGET_DIR)/usr/share/aclocal \
		$(TARGET_DIR)/usr/lib/pkgconfig $(TARGET_DIR)/usr/share/pkgconfig \
		$(TARGET_DIR)/usr/lib/cmake $(TARGET_DIR)/usr/share/cmake
	find $(TARGET_DIR)/usr/{lib,share}/ -name '*.cmake' -print0 | xargs -0 rm -f
	find $(TARGET_DIR)/lib/ $(TARGET_DIR)/usr/lib/ $(TARGET_DIR)/usr/libexec/ \
		\( -name '*.a' -o -name '*.la' \) -print0 | xargs -0 rm -f
ifneq ($(BR2_PACKAGE_GDB),y)
	rm -rf $(TARGET_DIR)/usr/share/gdb
endif
ifneq ($(BR2_PACKAGE_BASH),y)
	rm -rf $(TARGET_DIR)/usr/share/bash-completion
endif
ifneq ($(BR2_PACKAGE_ZSH),y)
	rm -rf $(TARGET_DIR)/usr/share/zsh
endif
	rm -rf $(TARGET_DIR)/usr/man $(TARGET_DIR)/usr/share/man
	rm -rf $(TARGET_DIR)/usr/info $(TARGET_DIR)/usr/share/info
	rm -rf $(TARGET_DIR)/usr/doc $(TARGET_DIR)/usr/share/doc
	rm -rf $(TARGET_DIR)/usr/share/gtk-doc
	rmdir $(TARGET_DIR)/usr/share 2>/dev/null || true
	$(STRIP_FIND_CMD) | xargs -0 $(STRIPCMD) 2>/dev/null || true
	$(STRIP_FIND_SPECIAL_LIBS_CMD) | xargs -0 -r $(STRIPCMD) $(STRIP_STRIP_DEBUG) 2>/dev/null || true

	test -f $(TARGET_DIR)/etc/ld.so.conf && \
		{ echo "ERROR: we shouldn't have a /etc/ld.so.conf file"; exit 1; } || true
	test -d $(TARGET_DIR)/etc/ld.so.conf.d && \
		{ echo "ERROR: we shouldn't have a /etc/ld.so.conf.d directory"; exit 1; } || true
	mkdir -p $(TARGET_DIR)/etc
	( \
		echo "NAME=Buildroot"; \
		echo "VERSION=$(BR2_VERSION_FULL)"; \
		echo "ID=buildroot"; \
		echo "VERSION_ID=$(BR2_VERSION)"; \
		echo "PRETTY_NAME=\"Buildroot $(BR2_VERSION)\"" \
	) >  $(TARGET_DIR)/usr/lib/os-release
	ln -sf ../usr/lib/os-release $(TARGET_DIR)/etc

	@$(call MESSAGE,"Sanitizing RPATH in target tree")
	$(TOPDIR)/support/scripts/fix-rpath target

# For a merged /usr, ensure that /lib, /bin and /sbin and their /usr
# counterparts are appropriately setup as symlinks ones to the others.
ifeq ($(BR2_ROOTFS_MERGED_USR),y)

	@$(foreach d, $(call qstrip,$(BR2_ROOTFS_OVERLAY)), \
		$(call MESSAGE,"Sanity check in overlay $(d)"); \
		not_merged_dirs="$$(support/scripts/check-merged-usr.sh $(d))"; \
		test -n "$$not_merged_dirs" && { \
			echo "ERROR: The overlay in $(d) is not" \
				"using a merged /usr for the following directories:" \
				$$not_merged_dirs; \
			exit 1; \
		} || true$(sep))

endif # merged /usr

	@$(foreach d, $(call qstrip,$(BR2_ROOTFS_OVERLAY)), \
		$(call MESSAGE,"Copying overlay $(d)"); \
		$(call SYSTEM_RSYNC,$(d),$(TARGET_DIR))$(sep))

	@$(foreach s, $(call qstrip,$(BR2_ROOTFS_POST_BUILD_SCRIPT)), \
		$(call MESSAGE,"Executing post-build script $(s)"); \
		$(EXTRA_ENV) $(s) $(TARGET_DIR) $(call qstrip,$(BR2_ROOTFS_POST_SCRIPT_ARGS))$(sep))

	touch $(TARGET_DIR)/usr

.PHONY: target-post-image
target-post-image: $(TARGETS_ROOTFS) target-finalize staging-finalize
	@rm -f $(ROOTFS_COMMON_TAR)
	$(Q)mkdir -p $(BINARIES_DIR)
	@$(foreach s, $(call qstrip,$(BR2_ROOTFS_POST_IMAGE_SCRIPT)), \
		$(call MESSAGE,"Executing post-image script $(s)"); \
		$(EXTRA_ENV) $(s) $(BINARIES_DIR) $(call qstrip,$(BR2_ROOTFS_POST_SCRIPT_ARGS))$(sep))

.PHONY: source
source: $(foreach p,$(PACKAGES),$(p)-all-source)

.PHONY: _external-deps external-deps
_external-deps: $(foreach p,$(PACKAGES),$(p)-all-external-deps)
external-deps:
	@$(MAKE1) -Bs $(EXTRAMAKEARGS) _external-deps | sort -u

.PHONY: legal-info-clean
legal-info-clean:
	@rm -fr $(LEGAL_INFO_DIR)

.PHONY: legal-info-prepare
legal-info-prepare: $(LEGAL_INFO_DIR)
	@$(call MESSAGE,"Buildroot $(BR2_VERSION_FULL) Collecting legal info")
	@$(call legal-license-file,buildroot,buildroot,support/legal-info/buildroot.hash,COPYING,COPYING,HOST)
	@$(call legal-manifest,TARGET,PACKAGE,VERSION,LICENSE,LICENSE FILES,SOURCE ARCHIVE,SOURCE SITE,DEPENDENCIES WITH LICENSES)
	@$(call legal-manifest,HOST,PACKAGE,VERSION,LICENSE,LICENSE FILES,SOURCE ARCHIVE,SOURCE SITE,DEPENDENCIES WITH LICENSES)
	@$(call legal-manifest,HOST,buildroot,$(BR2_VERSION_FULL),GPL-2.0+,COPYING,not saved,not saved)
	@$(call legal-warning,the Buildroot source code has not been saved)
	@cp $(BR2_CONFIG) $(LEGAL_INFO_DIR)/buildroot.config

.PHONY: legal-info
legal-info: legal-info-clean legal-info-prepare $(foreach p,$(PACKAGES),$(p)-all-legal-info) \
		$(REDIST_SOURCES_DIR_TARGET) $(REDIST_SOURCES_DIR_HOST)
	@cat support/legal-info/README.header >>$(LEGAL_REPORT)
	@if [ -r $(LEGAL_WARNINGS) ]; then \
		cat support/legal-info/README.warnings-header \
			$(LEGAL_WARNINGS) >>$(LEGAL_REPORT); \
		cat $(LEGAL_WARNINGS); fi
	@rm -f $(LEGAL_WARNINGS)
	@(cd $(LEGAL_INFO_DIR); \
		find * -type f -exec sha256sum {} + | LC_ALL=C sort -k2 \
			>.legal-info.sha256; \
		mv .legal-info.sha256 legal-info.sha256)
	@echo "Legal info produced in $(LEGAL_INFO_DIR)"

.PHONY: show-targets
show-targets:
	@echo $(sort $(PACKAGES)) $(sort $(TARGETS_ROOTFS))

.PHONY: show-build-order
show-build-order: $(patsubst %,%-show-build-order,$(PACKAGES))

.PHONY: graph-build
graph-build: $(O)/build/build-time.log
	@install -d $(GRAPHS_DIR)
	$(foreach o,name build duration,./support/scripts/graph-build-time \
					--type=histogram --order=$(o) --input=$(<) \
					--output=$(GRAPHS_DIR)/build.hist-$(o).$(BR_GRAPH_OUT) \
					$(if $(BR2_GRAPH_ALT),--alternate-colors)$(sep))
	$(foreach t,packages steps,./support/scripts/graph-build-time \
				   --type=pie-$(t) --input=$(<) \
				   --output=$(GRAPHS_DIR)/build.pie-$(t).$(BR_GRAPH_OUT) \
				   $(if $(BR2_GRAPH_ALT),--alternate-colors)$(sep))

.PHONY: graph-depends-requirements
graph-depends-requirements:
	@dot -? >/dev/null 2>&1 || \
		{ echo "ERROR: The 'dot' program from Graphviz is needed for graph-depends" >&2; exit 1; }

.PHONY: graph-depends
graph-depends: graph-depends-requirements
	@$(INSTALL) -d $(GRAPHS_DIR)
	@cd "$(CONFIG_DIR)"; \
	$(TOPDIR)/support/scripts/graph-depends $(BR2_GRAPH_DEPS_OPTS) \
		--direct -o $(GRAPHS_DIR)/$(@).dot
	dot $(BR2_GRAPH_DOT_OPTS) -T$(BR_GRAPH_OUT) \
		-o $(GRAPHS_DIR)/$(@).$(BR_GRAPH_OUT) \
		$(GRAPHS_DIR)/$(@).dot

.PHONY: graph-size
graph-size:
	$(Q)mkdir -p $(GRAPHS_DIR)
	$(Q)$(TOPDIR)/support/scripts/size-stats --builddir $(BASE_DIR) \
		--graph $(GRAPHS_DIR)/graph-size.$(BR_GRAPH_OUT) \
		--file-size-csv $(GRAPHS_DIR)/file-size-stats.csv \
		--package-size-csv $(GRAPHS_DIR)/package-size-stats.csv

.PHONY: check-dependencies
check-dependencies:
	@cd "$(CONFIG_DIR)"; \
	$(TOPDIR)/support/scripts/graph-depends -C

.PHONY: show-info
show-info:
	@:
	$(info $(call clean-json, \
			{ $(foreach p, \
				$(sort $(foreach i,$(PACKAGES) $(TARGETS_ROOTFS), \
						$(i) \
						$($(call UPPERCASE,$(i))_FINAL_RECURSIVE_DEPENDENCIES) \
					) \
				), \
				$(call json-info,$(call UPPERCASE,$(p)))$(comma) \
			) } \
		) \
	)

else # ifeq ($(BR2_HAVE_DOT_CONFIG),y)

# Some subdirectories are also package names. To avoid that "make linux"
# on an unconfigured tree produces "Nothing to be done", add an explicit
# rule for it.
# Also for 'all' we error out and ask the user to configure first.
.PHONY: linux toolchain
linux toolchain all: outputmakefile
	$(error Please configure Buildroot first (e.g. "make menuconfig"))
	@exit 1

endif # ifeq ($(BR2_HAVE_DOT_CONFIG),y)

# configuration
# ---------------------------------------------------------------------------

HOSTCFLAGS = $(CFLAGS_FOR_BUILD)
export HOSTCFLAGS

$(BUILD_DIR)/buildroot-config/%onf:
	mkdir -p $(@D)/lxdialog
	PKG_CONFIG_PATH="$(HOST_PKG_CONFIG_PATH)" $(MAKE) CC="$(HOSTCC_NOCCACHE)" HOSTCC="$(HOSTCC_NOCCACHE)" \
	    obj=$(@D) -C $(CONFIG) -f Makefile.br $(@F)

DEFCONFIG = $(call qstrip,$(BR2_DEFCONFIG))

# We don't want to fully expand BR2_DEFCONFIG here, so Kconfig will
# recognize that if it's still at its default $(CONFIG_DIR)/defconfig
COMMON_CONFIG_ENV = \
	BR2_DEFCONFIG='$(call qstrip,$(value BR2_DEFCONFIG))' \
	KCONFIG_AUTOCONFIG=$(BUILD_DIR)/buildroot-config/auto.conf \
	KCONFIG_AUTOHEADER=$(BUILD_DIR)/buildroot-config/autoconf.h \
	KCONFIG_TRISTATE=$(BUILD_DIR)/buildroot-config/tristate.config \
	BR2_CONFIG=$(BR2_CONFIG) \
	HOST_GCC_VERSION="$(HOSTCC_VERSION)" \
	BASE_DIR=$(BASE_DIR) \
	SKIP_LEGACY=

xconfig: $(BUILD_DIR)/buildroot-config/qconf outputmakefile
	@$(COMMON_CONFIG_ENV) $< $(CONFIG_CONFIG_IN)

gconfig: $(BUILD_DIR)/buildroot-config/gconf outputmakefile
	@$(COMMON_CONFIG_ENV) srctree=$(TOPDIR) $< $(CONFIG_CONFIG_IN)

menuconfig: $(BUILD_DIR)/buildroot-config/mconf outputmakefile
	@$(COMMON_CONFIG_ENV) $< $(CONFIG_CONFIG_IN)

nconfig: $(BUILD_DIR)/buildroot-config/nconf outputmakefile
	@$(COMMON_CONFIG_ENV) $< $(CONFIG_CONFIG_IN)

config: $(BUILD_DIR)/buildroot-config/conf outputmakefile
	@$(COMMON_CONFIG_ENV) $< $(CONFIG_CONFIG_IN)

# For the config targets that automatically select options, we pass
# SKIP_LEGACY=y to disable the legacy options. However, in that case
# no values are set for the legacy options so a subsequent oldconfig
# will query them. Therefore, run an additional olddefconfig.

randconfig allyesconfig alldefconfig allnoconfig: $(BUILD_DIR)/buildroot-config/conf outputmakefile
	@$(COMMON_CONFIG_ENV) SKIP_LEGACY=y $< --$@ $(CONFIG_CONFIG_IN)
	@$(COMMON_CONFIG_ENV) $< --olddefconfig $(CONFIG_CONFIG_IN) >/dev/null

randpackageconfig allyespackageconfig allnopackageconfig: $(BUILD_DIR)/buildroot-config/conf outputmakefile
	@grep -v BR2_PACKAGE_ $(BR2_CONFIG) > $(CONFIG_DIR)/.config.nopkg
	@$(COMMON_CONFIG_ENV) SKIP_LEGACY=y \
		KCONFIG_ALLCONFIG=$(CONFIG_DIR)/.config.nopkg \
		$< --$(subst package,,$@) $(CONFIG_CONFIG_IN)
	@rm -f $(CONFIG_DIR)/.config.nopkg
	@$(COMMON_CONFIG_ENV) $< --olddefconfig $(CONFIG_CONFIG_IN) >/dev/null

oldconfig syncconfig olddefconfig: $(BUILD_DIR)/buildroot-config/conf outputmakefile
	@$(COMMON_CONFIG_ENV) $< --$@ $(CONFIG_CONFIG_IN)

defconfig: $(BUILD_DIR)/buildroot-config/conf outputmakefile
	@$(COMMON_CONFIG_ENV) $< --defconfig$(if $(DEFCONFIG),=$(DEFCONFIG)) $(CONFIG_CONFIG_IN)

define percent_defconfig
# Override the BR2_DEFCONFIG from COMMON_CONFIG_ENV with the new defconfig
%_defconfig: $(BUILD_DIR)/buildroot-config/conf $(1)/configs/%_defconfig outputmakefile
	@$$(COMMON_CONFIG_ENV) BR2_DEFCONFIG=$(1)/configs/$$@ \
		$$< --defconfig=$(1)/configs/$$@ $$(CONFIG_CONFIG_IN)
endef
$(eval $(foreach d,$(call reverse,$(TOPDIR) $(BR2_EXTERNAL_DIRS)),$(call percent_defconfig,$(d))$(sep)))

update-defconfig: savedefconfig

savedefconfig: $(BUILD_DIR)/buildroot-config/conf outputmakefile
	@$(COMMON_CONFIG_ENV) $< \
		--savedefconfig=$(if $(DEFCONFIG),$(DEFCONFIG),$(CONFIG_DIR)/defconfig) \
		$(CONFIG_CONFIG_IN)
	@$(SED) '/BR2_DEFCONFIG=/d' $(if $(DEFCONFIG),$(DEFCONFIG),$(CONFIG_DIR)/defconfig)

.PHONY: defconfig savedefconfig update-defconfig

################################################################################
#
# Cleanup and misc junk
#
################################################################################

# staging and target directories do NOT list these as
# dependencies anywhere else
$(BUILD_DIR) $(BASE_TARGET_DIR) $(HOST_DIR) $(BINARIES_DIR) $(LEGAL_INFO_DIR) $(REDIST_SOURCES_DIR_TARGET) $(REDIST_SOURCES_DIR_HOST):
	@mkdir -p $@

# outputmakefile generates a Makefile in the output directory, if using a
# separate output directory. This allows convenient use of make in the
# output directory.
.PHONY: outputmakefile
outputmakefile:
ifeq ($(NEED_WRAPPER),y)
	$(Q)$(TOPDIR)/support/scripts/mkmakefile $(TOPDIR) $(O)
endif

# printvars prints all the variables currently defined in our
# Makefiles. Alternatively, if a non-empty VARS variable is passed,
# only the variables matching the make pattern passed in VARS are
# displayed.
.PHONY: printvars
printvars:
	@:
	$(foreach V, \
		$(sort $(filter $(VARS),$(.VARIABLES))), \
		$(if $(filter-out environment% default automatic, \
				$(origin $V)), \
		$(if $(QUOTED_VARS),\
			$(info $V='$(subst ','\'',$(if $(RAW_VARS),$(value $V),$($V)))'), \
			$(info $V=$(if $(RAW_VARS),$(value $V),$($V))))))
# ' Syntax colouring...

.PHONY: clean
clean:
	rm -rf $(BASE_TARGET_DIR) $(BINARIES_DIR) $(HOST_DIR) $(HOST_DIR_SYMLINK) \
		$(BUILD_DIR) $(BASE_DIR)/staging \
		$(LEGAL_INFO_DIR) $(GRAPHS_DIR)

.PHONY: distclean
distclean: clean
ifeq ($(O),$(CURDIR)/output)
	rm -rf $(O)
endif
	rm -rf $(TOPDIR)/dl $(BR2_CONFIG) $(CONFIG_DIR)/.config.old $(CONFIG_DIR)/..config.tmp \
		$(CONFIG_DIR)/.auto.deps $(BASE_DIR)/.br2-external.*

.PHONY: help
help:
	@echo 'Cleaning:'
	@echo '  clean                  - delete all files created by build'
	@echo '  distclean              - delete all non-source files (including .config)'
	@echo
	@echo 'Build:'
	@echo '  all                    - make world'
	@echo '  toolchain              - build toolchain'
	@echo '  sdk                    - build relocatable SDK'
	@echo
	@echo 'Configuration:'
	@echo '  menuconfig             - interactive curses-based configurator'
	@echo '  nconfig                - interactive ncurses-based configurator'
	@echo '  xconfig                - interactive Qt-based configurator'
	@echo '  gconfig                - interactive GTK-based configurator'
	@echo '  oldconfig              - resolve any unresolved symbols in .config'
	@echo '  syncconfig             - Same as oldconfig, but quietly, additionally update deps'
	@echo '  olddefconfig           - Same as syncconfig but sets new symbols to their default value'
	@echo '  randconfig             - New config with random answer to all options'
	@echo '  defconfig              - New config with default answer to all options;'
	@echo '                             BR2_DEFCONFIG, if set on the command line, is used as input'
	@echo '  savedefconfig          - Save current config to BR2_DEFCONFIG (minimal config)'
	@echo '  update-defconfig       - Same as savedefconfig'
	@echo '  allyesconfig           - New config where all options are accepted with yes'
	@echo '  allnoconfig            - New config where all options are answered with no'
	@echo '  alldefconfig           - New config where all options are set to default'
	@echo '  randpackageconfig      - New config with random answer to package options'
	@echo '  allyespackageconfig    - New config where pkg options are accepted with yes'
	@echo '  allnopackageconfig     - New config where package options are answered with no'
	@echo
	@echo 'Package-specific:'
	@echo '  <pkg>                  - Build and install <pkg> and all its dependencies'
	@echo '  <pkg>-source           - Only download the source files for <pkg>'
	@echo '  <pkg>-extract          - Extract <pkg> sources'
	@echo '  <pkg>-patch            - Apply patches to <pkg>'
	@echo '  <pkg>-depends          - Build <pkg>'\''s dependencies'
	@echo '  <pkg>-configure        - Build <pkg> up to the configure step'
	@echo '  <pkg>-build            - Build <pkg> up to the build step'
	@echo '  <pkg>-show-info        - generate info about <pkg>, as a JSON blurb'
	@echo '  <pkg>-show-depends     - List packages on which <pkg> depends'
	@echo '  <pkg>-show-rdepends    - List packages which have <pkg> as a dependency'
	@echo '  <pkg>-show-recursive-depends'
	@echo '                         - Recursively list packages on which <pkg> depends'
	@echo '  <pkg>-show-recursive-rdepends'
	@echo '                         - Recursively list packages which have <pkg> as a dependency'
	@echo '  <pkg>-graph-depends    - Generate a graph of <pkg>'\''s dependencies'
	@echo '  <pkg>-graph-rdepends   - Generate a graph of <pkg>'\''s reverse dependencies'
	@echo '  <pkg>-dirclean         - Remove <pkg> build directory'
	@echo '  <pkg>-reconfigure      - Restart the build from the configure step'
	@echo '  <pkg>-rebuild          - Restart the build from the build step'
	$(foreach p,$(HELP_PACKAGES), \
		@echo $(sep) \
		@echo '$($(p)_NAME):' $(sep) \
		$($(p)_HELP_CMDS)$(sep))
	@echo
	@echo 'Documentation:'
	@echo '  manual                 - build manual in all formats'
	@echo '  manual-html            - build manual in HTML'
	@echo '  manual-split-html      - build manual in split HTML'
	@echo '  manual-pdf             - build manual in PDF'
	@echo '  manual-text            - build manual in text'
	@echo '  manual-epub            - build manual in ePub'
	@echo '  graph-build            - generate graphs of the build times'
	@echo '  graph-depends          - generate graph of the dependency tree'
	@echo '  graph-size             - generate stats of the filesystem size'
	@echo '  list-defconfigs        - list all defconfigs (pre-configured minimal systems)'
	@echo
	@echo 'Miscellaneous:'
	@echo '  source                 - download all sources needed for offline-build'
	@echo '  external-deps          - list external packages used'
	@echo '  legal-info             - generate info about license compliance'
	@echo '  show-info              - generate info about packages, as a JSON blurb'
	@echo '  printvars              - dump internal variables selected with VARS=...'
	@echo
	@echo '  make V=0|1             - 0 => quiet build (default), 1 => verbose build'
	@echo '  make O=dir             - Locate all output files in "dir", including .config'
	@echo
	@echo 'For further details, see README, generate the Buildroot manual, or consult'
	@echo 'it on-line at http://buildroot.org/docs.html'
	@echo

# List the defconfig files
# $(1): base directory
# $(2): br2-external name, empty for bundled
define list-defconfigs
	@first=true; \
	for defconfig in $(1)/configs/*_defconfig; do \
		[ -f "$${defconfig}" ] || continue; \
		if $${first}; then \
			if [ "$(2)" ]; then \
				printf 'External configs in "$(call qstrip,$(2))":\n'; \
			else \
				printf "Built-in configs:\n"; \
			fi; \
			first=false; \
		fi; \
		defconfig="$${defconfig##*/}"; \
		printf "  %-35s - Build for %s\n" "$${defconfig}" "$${defconfig%_defconfig}"; \
	done; \
	$${first} || printf "\n"
endef

# We iterate over BR2_EXTERNAL_NAMES rather than BR2_EXTERNAL_DIRS,
# because we want to display the name of the br2-external tree.
.PHONY: list-defconfigs
list-defconfigs:
	$(call list-defconfigs,$(TOPDIR))
	$(foreach name,$(BR2_EXTERNAL_NAMES),\
		$(call list-defconfigs,$(BR2_EXTERNAL_$(name)_PATH),\
			$(BR2_EXTERNAL_$(name)_DESC))$(sep))

release: OUT = buildroot-$(BR2_VERSION)

# Create release tarballs. We need to fiddle a bit to add the generated
# documentation to the git output
release:
	git archive --format=tar --prefix=$(OUT)/ HEAD > $(OUT).tar
	$(MAKE) O=$(OUT) manual-html manual-text manual-pdf
	$(MAKE) O=$(OUT) clean
	tar rf $(OUT).tar $(OUT)
	gzip -9 -c < $(OUT).tar > $(OUT).tar.gz
	bzip2 -9 -c < $(OUT).tar > $(OUT).tar.bz2
	rm -rf $(OUT) $(OUT).tar

print-version:
	@echo $(BR2_VERSION_FULL)

check-package:
	find $(TOPDIR) -type f \( -name '*.mk' -o -name '*.hash' -o -name 'Config.*' \) \
		-exec ./utils/check-package {} +

.PHONY: .gitlab-ci.yml
.gitlab-ci.yml: .gitlab-ci.yml.in
	./support/scripts/generate-gitlab-ci-yml $< > $@

include docs/manual/manual.mk
-include $(foreach dir,$(BR2_EXTERNAL_DIRS),$(sort $(wildcard $(dir)/docs/*/*.mk)))

.PHONY: $(noconfig_targets)

endif #umask / $(CURDIR) / $(O)
