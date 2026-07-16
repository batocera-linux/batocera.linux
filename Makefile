# We want bash as shell
SHELL := $(shell if [ -x "$$BASH" ]; then echo $$BASH; \
	 else command -v bash 2>/dev/null; \
	 fi)

ifeq ($(SHELL),)
$(error Bash shell not found)
endif

# We want make 4.3+
ifneq ($(shell echo $$'4.3\n$(MAKE_VERSION)' | sort -V | head -n1),4.3)
$(error GNU Make 4.3 or higher is required, you are using $(MAKE_VERSION))
endif

# We don't use any of the default rules (including suffix rules),
# so disable them
MAKEFLAGS += --no-builtin-rules
.SUFFIXES:

# This is our default rule, so it must come first
.PHONY: vars
vars:

OS := $(shell uname)

ifeq ($(OS),Darwin)
FIND ?= gfind
NPROC := $(shell sysctl -n hw.ncpu)
else
FIND ?= find
NPROC := $(shell nproc)
endif

PROJECT_DIR    := $(realpath $(CURDIR))
DL_DIR         ?= $(PROJECT_DIR)/dl
OUTPUT_DIR     ?= $(PROJECT_DIR)/output
CCACHE_DIR     ?= $(PROJECT_DIR)/buildroot-ccache
LOCAL_MK       ?= $(PROJECT_DIR)/batocera.mk
EXTRA_OPTS     ?=
MAKE_JLEVEL    ?= $(NPROC)
MAKE_LLEVEL    ?= $(NPROC)
BATCH_MODE     ?=
PARALLEL_BUILD ?=
DIRECT_BUILD   ?=
DAYS           ?= 1
SYSTEMS_REPORT_EXCLUDE_TARGETS ?= bcm2835 jh7110
SYSTEMS_REPORT_PARALLEL ?= y

## BEGIN helper macros

USER_DEFCONFIG := $(PROJECT_DIR)/configs/.user_defconfig

# Macro to append a line to the user defconfig file
define add-defconfig
$(file >>$(USER_DEFCONFIG),$(1))
endef

REQUIRE = $(if $(shell command -v $(1) 2>/dev/null),,$(error $(1) not found$(if $(2),; $(2))))
UC = $(shell echo '$1' | tr '[:lower:]' '[:upper:]')

TERM_BOLD := $(shell tput smso 2>/dev/null)
TERM_RESET := $(shell tput rmso 2>/dev/null)
TERM_URL = \e]8;;$(1)\e\\$(if $(2),$(2),$(1))\e]8;;\e\\
MESSAGE = printf '$(TERM_BOLD)>>> $(if $*,$*: ,)%b$(TERM_RESET)\n' $$'$(call strip,$(subst ',\',$(1)))'

# END helper macros

# Clear the user defconfig file at the start before including
# the user's makefile customizations
$(file >$(USER_DEFCONFIG),)

-include $(LOCAL_MK)
include $(PROJECT_DIR)/docker/docker.mk

ifdef EXTRA_OPTS
$(warning EXTRA_OPTS will be removed in the future, please migrate to $$(call add-defconfig,...))
$(foreach opt,$(EXTRA_OPTS),$(call add-defconfig,$(subst \",",$(opt))))
endif

ifdef PARALLEL_BUILD
$(call add-defconfig,BR2_PER_PACKAGE_DIRECTORIES=y)
$(call add-defconfig,BR2_JLEVEL=$(MAKE_JLEVEL))
MAKE_OPTS  += -j$(MAKE_JLEVEL)
MAKE_OPTS  += -l$(MAKE_LLEVEL)
endif

ifeq ($(SYSTEMS_REPORT_PARALLEL),y)
ifneq ($(PARALLEL_BUILD),y)
SYSTEMS_REPORT_MAKE_OPTS += BR2_PER_PACKAGE_DIRECTORIES=y
SYSTEMS_REPORT_MAKE_OPTS += BR2_JLEVEL=$(MAKE_JLEVEL)
SYSTEMS_REPORT_MAKE_OPTS  += -j$(MAKE_JLEVEL)
SYSTEMS_REPORT_MAKE_OPTS  += -l$(MAKE_LLEVEL)
endif
endif

# List of packages that are always good to rebuild for versioning/stamps etc
MANDATORY_REBUILD_PKGS := batocera-es-system batocera-configgen batocera-system batocera-splash

# All supported targets based on the board files in configs/, sorted for consistency
TARGETS := $(sort $(patsubst batocera-%.board,%,$(notdir $(wildcard $(PROJECT_DIR)/configs/*.board))))

# All supported targets for systems report generation
SYSTEMS_REPORT_TARGETS := $(filter-out $(SYSTEMS_REPORT_EXCLUDE_TARGETS) x86_wow64,$(TARGETS))

# All defconfig files for systems report targets, generated from the board files
SYSTEMS_REPORT_DEFCONFIGS = $(foreach target,$(SYSTEMS_REPORT_TARGETS),$(call target-defconfig,$(target)))

# define build command based on whether we are building direct or inside a docker build container
ifdef DIRECT_BUILD
define MAKE_BUILDROOT
	make $(MAKE_OPTS) O=$(OUTPUT_DIR)/$(1) \
		BR2_EXTERNAL=$(PROJECT_DIR) \
		BR2_DL_DIR=$(DL_DIR) \
		BR2_CCACHE_DIR=$(CCACHE_DIR) \
		-C $(PROJECT_DIR)/buildroot
endef
else # DIRECT_BUILD
define MAKE_BUILDROOT
	$(call RUN_DOCKER,$(1)) make $(MAKE_OPTS) O=/$(1) \
					BR2_EXTERNAL=/build \
					-C /build/buildroot
endef
endif # DIRECT_BUILD

define MAKE_BUILDROOT_TARGET
	$(call MAKE_BUILDROOT,$*)
endef

.PHONY: help
help:
	@echo 'Information:'
	@echo '  vars                          - show current build configuration and settings'
	@echo '  <target>-build-cmd            - show the buildroot make command for <target>'
	@echo
	@echo 'Build:'
	@echo '  <target>-defconfig            - generate the defconfig file for <target>'
	@echo '  <target>-config               - generate defconfig and configure buildroot for <target>'
	@echo '  <target>-build                - configure and build <target>'
	@echo '  <target>-source               - download all sources needed for <target>'
	@echo '  <target>-show-build-order     - show the package build order for <target>'
	@echo '  <target>-kernel               - run kernel menuconfig for <target>'
	@echo '  <target>-graph-depends        - generate dependency graph (SVG) for <target>'
	@echo '  <target>-shell                - open a shell in the build environment for <target>'
	@echo '                                  use CMD=<cmd> to run a command (required in BATCH_MODE)'
	@echo '  <target>-pkg                  - build a single package for <target> (set PKG=<pkg>)'
	@echo
	@echo 'Cleaning:'
	@echo '  <target>-clean                - clean the build output and remove defconfig for <target>'
	@echo '  <target>-cleanbuild           - clean and rebuild <target> from scratch'
	@echo
	@echo 'Incremental rebuild:'
	@echo '  <target>-refresh              - surgically reset recently changed packages and rebuild'
	@echo '                                  (requires PARALLEL_BUILD=y, uses DAYS=<n> to control scope)'
	@echo '  <target>-clean-for-refresh    - reset recently changed packages without rebuilding'
	@echo
	@echo 'Deployment:'
	@echo '  <target>-flash                - flash a built image to a device (set DEV=<device>)'
	@echo '  <target>-upgrade              - upgrade boot partition on a device (set DEV=<device>)'
	@echo '  <target>-rsync                - rsync target filesystem to a remote device'
	@echo '                                  (set <TARGET>_IP=<ip>)'
	@echo '  <target>-webserver            - serve built images via HTTP (set BOARD=<board> to override)'
	@echo
	@echo 'Caching and snapshots:'
	@echo '  <target>-ccache-stats         - show ccache statistics for <target>'
	@echo '  <target>-snapshot             - create a btrfs snapshot of the build output'
	@echo '  <target>-rollback             - restore build output from a btrfs snapshot'
	@echo '  <target>-toolchain            - build toolchain+llvm and snapshot (requires btrfs)'
	@echo
	@echo 'Maintenance:'
	@echo '  <target>-find-build-dups      - list duplicate packages in the build directory'
	@echo '  <target>-remove-build-dups    - remove duplicate packages from the build directory'
	@echo '  find-dl-dups                  - list duplicate downloads in the download directory'
	@echo '  remove-dl-dups                - remove duplicate downloads from the download directory'
	@echo '  <target>-tail                 - tail the build-time log for <target>'
	@echo
	@echo 'Localization:'
	@echo '  <target>-update-po-files      - update translation files for <target>'
	@echo
	@echo 'Systems report:'
	@echo '  systems-report                - generate a systems report'
	@echo '  systems-report-clean          - remove a previously generated systems report'
	@echo '  systems-report-refresh        - clean and generate a systems report'
	@echo '  systems-report-serve          - serve a generated systems report via HTTP'
	@echo
	@echo 'Docker:'
	@echo '  pull-docker-image             - pull the build Docker image from the registry'
	@echo '  build-docker-image            - build the Docker image locally from Dockerfile'
	@echo '  update-docker-image           - clean stamp and re-pull the Docker image'
	@echo '  rebuild-docker-image          - clean stamp and rebuild the Docker image locally'
	@echo '  publish-docker-image          - push the Docker image to the registry'
	@echo '  clean-for-docker-image        - remove the Docker image availability stamp'
	@echo
	@echo 'Serial:'
	@echo '  uart                          - open a serial console (set SERIAL_DEV and SERIAL_BAUDRATE)'
	@echo
	@echo 'Environment variables:'
	@echo '  DIRECT_BUILD=1                - build natively instead of inside Docker'
	@echo '  PARALLEL_BUILD=1              - enable per-package directories and parallel build'
	@echo '  BATCH_MODE=1                  - non-interactive Docker mode'
	@echo '  EXTRA_OPTS="..."              - extra defconfig options (deprecated, use add-defconfig)'
	@echo '  PKG=<pkg>                     - package name for <target>-pkg'
	@echo '  CMD=<cmd>                     - command for <target>-shell or <target>-build'
	@echo '  DAYS=<n>                      - number of days to look back for <target>-refresh (default: 1)'
	@echo '  DEV=<device>                  - device path for <target>-flash and <target>-upgrade'
	@echo '  DOCKER=<cmd>                  - Docker command to use (default: docker)'
	@echo '  DOCKER_OPTS="..."             - additional Docker run options'
	@echo '  DOCKER_REPO=<repo>            - Docker image repository (default: batoceralinux)'
	@echo '  DOCKER_IMAGE_NAME=<name>      - Docker image name (default: batocera.linux-build)'
	@echo
	@echo 'Supported targets: $(TARGETS)'
	@echo
	@echo 'Example usage:'
	@echo '  make x86_64-build             - build the x86_64 target'
	@echo '  make x86_64-pkg PKG=linux     - rebuild only the linux package for x86_64'
	@echo '  make x86_64-shell CMD=bash    - open a bash shell in the x86_64 build environment'

vars:
	@echo "Supported targets:  $(TARGETS)"
	@echo "Project directory:  $(PROJECT_DIR)"
	@echo "Download directory: $(DL_DIR)"
	@echo "Build directory:    $(OUTPUT_DIR)"
	@echo "ccache directory:   $(CCACHE_DIR)"
	@echo "Extra defconfig:"
	@sed -e '/^\s*$$/d' -e 's/^/  /' "$(USER_DEFCONFIG)"
ifndef DIRECT_BUILD
	@echo "Docker repo/image:  $(DOCKER_IMAGE)"
	@echo "Docker options:     $(DOCKER_OPTS)"
endif
	@echo "Make options:       $(MAKE_OPTS)"

.PHONY: _check_find
_check_find:
ifeq ($(OS),Darwin)
	$(call REQUIRE,gfind,Please install findutils from Homebrew)
endif

# Target macros for files or directories (actual files)
target-output-dir = $(OUTPUT_DIR)/$(1)
target-board-file = $(PROJECT_DIR)/configs/batocera-$(1).board
target-defconfig = $(PROJECT_DIR)/configs/batocera-$(1)_defconfig

# File patterns for generated files based on target macros
TARGET_OUTPUT_DIR_PATTERN = $(call target-output-dir,%)
TARGET_BOARD_FILE_PATTERN = $(call target-board-file,%)
TARGET_DEFCONFIG_PATTERN = $(call target-defconfig,%)

# Macros for getting the $* equivalent file or directory
TARGET_OUTPUT_DIR = $(call target-output-dir,$*)
TARGET_BOARD_FILE = $(call target-board-file,$*)
TARGET_DEFCONFIG = $(call target-defconfig,$*)

# Stamp files (used for sequencing)
CCACHE_DIR_INITIALIZED = $(CCACHE_DIR)/.stamp_initialized
DL_DIR_INITIALIZED = $(DL_DIR)/.stamp_initialized
TARGET_OUTPUT_DIR_INITIALIZED = $(TARGET_OUTPUT_DIR_PATTERN)/.stamp_initialized

# Stamp pattern rules for initializing directories, ensuring they are
# only created once and can be used as dependencies for sequencing
.PRECIOUS: %/.stamp_initialized
%/.stamp_initialized:
	@mkdir -p $(@D)
	@touch $@

.PRECIOUS: $(TARGET_DEFCONFIG_PATTERN)
$(TARGET_DEFCONFIG_PATTERN): $(TARGET_BOARD_FILE_PATTERN) \
			     $(PROJECT_DIR)/configs/batocera-board.common \
			     $(wildcard $(PROJECT_DIR)/configs/batocera-board.local.common) \
			     $(USER_DEFCONFIG)
	@$(PROJECT_DIR)/configs/createDefconfig.sh \
		$(TARGET_BOARD_FILE) \
		$(USER_DEFCONFIG) \
		$(TARGET_DEFCONFIG)

%-supported:
	$(if $(filter $*,$(TARGETS)),,$(error $* not supported))

%-clean: | $(DOCKER_IMAGE_AVAILABLE) $(DL_DIR_INITIALIZED) $(CCACHE_DIR_INITIALIZED) $(TARGET_OUTPUT_DIR_INITIALIZED)
	@$(call MESSAGE,Cleaning buildroot)
	@$(MAKE_BUILDROOT_TARGET) clean
	@if [ -f '$(TARGET_DEFCONFIG)' ]; then \
		echo "Removing config for $*..."; \
		rm -f '$(TARGET_DEFCONFIG)'; \
	fi

%-defconfig: $(TARGET_DEFCONFIG_PATTERN) | %-supported
	@:

%-config: %-defconfig | $(DOCKER_IMAGE_AVAILABLE) $(DL_DIR_INITIALIZED) $(CCACHE_DIR_INITIALIZED) $(TARGET_OUTPUT_DIR_INITIALIZED)
	@$(call MESSAGE,Generating buildroot makefile)
	@$(MAKE_BUILDROOT_TARGET) batocera-$*_defconfig

%-build: %-config
	@$(call MESSAGE,$(or $(BUILD_MESSAGE),Building $(or $(CMD),image)))
	@$(MAKE_BUILDROOT_TARGET) $(CMD)

%-source: %-config
	@$(call MESSAGE,Fetching source code for all packages)
	@$(MAKE_BUILDROOT_TARGET) source

%-show-build-order: %-config
	@$(MAKE_BUILDROOT_TARGET) show-build-order

%-kernel: %-config
	@$(MAKE_BUILDROOT_TARGET) linux-menuconfig

# force -j1 or graph-depends python script will bail
%-graph-depends: %-config
	@$(MAKE_BUILDROOT_TARGET) -j1 BR2_GRAPH_OUT=svg graph-depends

%-shell: %-config
ifdef BATCH_MODE
	$(if $(CMD),,$(error CMD is required to use $*-shell in BATCH_MODE))
endif
	@$(call MESSAGE,$(if $(CMD),Executing command,Starting interactive shell))
	@$(RUN_DOCKER_TARGET) $(CMD)

%-ccache-stats: %-config
	@$(MAKE_BUILDROOT_TARGET) ccache-stats

%-build-cmd: %-supported
	@echo $(MAKE_BUILDROOT_TARGET)

%-clean-for-refresh: %-supported | $(TARGET_OUTPUT_DIR_INITIALIZED)
ifndef PARALLEL_BUILD
	$(error PARALLEL_BUILD=y must be set for $*-refresh)
endif
	@$(call MESSAGE,Refresh & Targeted Rebuild Trigger (DAYS=$(DAYS)))
	@python3 $(PROJECT_DIR)/scripts/linux/refresh_resolver.py \
		--project-dir $(PROJECT_DIR) \
		--output-dir $(TARGET_OUTPUT_DIR) \
		--days $(DAYS) \
		--mandatory "$(MANDATORY_REBUILD_PKGS)"

	@$(call MESSAGE,Removing Host and Target directories)
	@for dir in include share lib/pkgconfig; do \
		if [ -d "$(TARGET_OUTPUT_DIR)/host/$$dir" ]; then \
			echo "Cleaning host staging: $$dir..."; \
			rm -rf $(TARGET_OUTPUT_DIR)/host/$$dir; \
		fi; \
	done
	@rm -rf $(TARGET_OUTPUT_DIR)/target

%-refresh: %-clean-for-refresh | $(DOCKER_IMAGE_AVAILABLE)
	@$(MAKE) $*-build

%-cleanbuild: %-clean
	@$(MAKE) $*-build

%-pkg: %-supported
	$(if $(PKG),,$(error PKG not specified))

	@$(MAKE) $*-build CMD=$(PKG) BUILD_MESSAGE="Building package $(PKG)"

%-webserver: %-supported | $(TARGET_OUTPUT_DIR_INITIALIZED)
	$(if $(wildcard $(TARGET_OUTPUT_DIR)/images/batocera/*),,$(error $* not built!))
	$(call REQUIRE,python3)
ifeq ($(strip $(BOARD)),)
	$(if $(wildcard $(TARGET_OUTPUT_DIR)/images/batocera/images/$*),,$(error Directory not found: $(TARGET_OUTPUT_DIR)/images/batocera/images/$*))
	python3 -m http.server --directory $(TARGET_OUTPUT_DIR)/images/batocera/images/$*/
else
	$(if $(wildcard $(TARGET_OUTPUT_DIR)/images/batocera/images/$(BOARD)),,$(error Directory not found: $(TARGET_OUTPUT_DIR)/images/batocera/images/$(BOARD)))
	python3 -m http.server --directory $(TARGET_OUTPUT_DIR)/images/batocera/images/$(BOARD)/
endif

%-rsync: %-supported | $(TARGET_OUTPUT_DIR_INITIALIZED)
	$(eval TMP := $(call UC, $*)_IP)
	$(call REQUIRE,rsync)
	$(if $($(TMP)),,$(error $(TMP) not set))
	rsync -e "ssh -o 'UserKnownHostsFile /dev/null' -o StrictHostKeyChecking=no" -av $(TARGET_OUTPUT_DIR)/target/ root@$($(TMP)):/

%-tail: %-supported
	@tail -F $(TARGET_OUTPUT_DIR)/build/build-time.log

%-snapshot: %-supported
	$(call REQUIRE,btrfs)
	@mkdir -p $(OUTPUT_DIR)/snapshots
	-@sudo btrfs sub del $(OUTPUT_DIR)/snapshots/$*-toolchain
	@btrfs subvolume snapshot -r $(TARGET_OUTPUT_DIR) $(OUTPUT_DIR)/snapshots/$*-toolchain

%-rollback: %-supported
	$(call REQUIRE,btrfs)
	-@sudo btrfs sub del $(TARGET_OUTPUT_DIR)
	@btrfs subvolume snapshot $(OUTPUT_DIR)/snapshots/$*-toolchain $(TARGET_OUTPUT_DIR)

%-flash: %-supported
	$(if $(DEV),,$(error DEV not specified))
	@gzip -dc $(TARGET_OUTPUT_DIR)/images/batocera/images/$*/batocera-*.img.gz | sudo dd of=$(DEV) bs=5M status=progress
	@sync

%-upgrade: %-supported
	$(if $(DEV),,$(error DEV not specified))
	-@sudo umount /tmp/mount
	-@mkdir -p /tmp/mount
	@sudo mount $(DEV)1 /tmp/mount
	@lsblk
	@ls /tmp/mount
	@echo "continue BATOCERA upgrade $(DEV)1 with $* build? [y/N]"
	@read line; if [ "$$line" != "y" ]; then echo aborting; exit 1 ; fi
	-@sudo rm /tmp/mount/boot/batocera
	@sudo tar xvf $(TARGET_OUTPUT_DIR)/images/batocera/images/$*/boot.tar.xz -C /tmp/mount --no-same-owner --exclude=batocera-boot.conf --exclude=config.txt
	@sudo umount /tmp/mount
	-@rmdir /tmp/mount
	@sudo fatlabel $(DEV)1 BATOCERA

%-toolchain: %-supported
	$(call REQUIRE,btrfs)
	-@sudo btrfs sub del $(TARGET_OUTPUT_DIR)
	@btrfs subvolume create $(TARGET_OUTPUT_DIR)
	@$(MAKE) $*-config
	@$(MAKE) $*-build CMD=toolchain
	@$(MAKE) $*-build CMD=llvm
	@$(MAKE) $*-snapshot

%-find-build-dups: %-supported _check_find
	@$(FIND) $(TARGET_OUTPUT_DIR)/build -maxdepth 1 -type d -printf '%T@ %p %f\n' | sed -r 's:\-[0-9a-f\.]+$$::' | sort -k3 -k1 | uniq -f 2 -d | cut -d' ' -f2

%-remove-build-dups: %-supported _check_find
	@while [ -n "`$(FIND) $(TARGET_OUTPUT_DIR)/build -maxdepth 1 -type d -printf '%T@ %p %f\n' | sed -r 's:\-[0-9a-f\.]+$$::' | sort -k3 -k1 | uniq -f 2 -d | cut -d' ' -f2 | grep .`" ]; do \
		$(FIND) $(TARGET_OUTPUT_DIR)/build -maxdepth 1 -type d -printf '%T@ %p %f\n' | sed -r 's:\-[0-9a-f\.]+$$::' | sort -k3 -k1 | uniq -f 2 -d | cut -d' ' -f2 | xargs rm -rf ; \
	done

.PHONY: find-dl-dups
find-dl-dups: _check_find
	@$(FIND) $(DL_DIR)/ -maxdepth 2 -type f -name "*.zip" -o -name "*.tar.*" -printf '%T@ %p %f\n' | sed -r 's:\-[-_0-9a-fvrgit\.]+(\.zip|\.tar\.[2a-z]+)$$::' | sort -k3 -k1 | uniq -f 2 -d | cut -d' ' -f2

.PHONY: remove-dl-dups
remove-dl-dups: _check_find
	@while [ -n "`$(FIND) $(DL_DIR)/ -maxdepth 2 -type f -name "*.zip" -o -name "*.tar.*" -printf '%T@ %p %f\n' | sed -r 's:\-[-_0-9a-fvrgit\.]+(\.zip|\.tar\.[2a-z]+)$$::' | sort -k3 -k1 | uniq -f 2 -d | cut -d' ' -f2 | grep .`" ] ; do \
		$(FIND) $(DL_DIR) -maxdepth 2 -type f -name "*.zip" -o -name "*.tar.*" -printf '%T@ %p %f\n' | sed -r 's:\-[-_0-9a-fvrgit\.]+(\.zip|\.tar\.[2a-z]+)$$::' | sort -k3 -k1 | uniq -f 2 -d | cut -d' ' -f2 | xargs rm -rf ; \
	done

.PHONY: uart
uart:
	$(call REQUIRE,picocom)
	$(if $(SERIAL_DEV),,$(error SERIAL_DEV not specified))
	$(if $(SERIAL_BAUDRATE),,$(error SERIAL_BAUDRATE not specified))
	$(if $(wildcard $(SERIAL_DEV)),,$(error $(SERIAL_DEV) not available))
	@picocom $(SERIAL_DEV) -b $(SERIAL_BAUDRATE)

%-update-po-files: %-config
	@$(call MESSAGE,Updating translation files)
	@$(MAKE_BUILDROOT_TARGET) update-po-files

# The systems report is generated by running the `systems-report-data` buildroot Makefile rule (which
# is defined in external.mk) with `$(OUTPUT_DIR)/systems-report` as the output directory. The last
# target (zen3, unless excluded) is used as the "board" for the buildroot environment. The generated
# data is then processed by the `batocera-systems-report` script in the project's virtual environment to
# produce the final report files.

ES_SYSTEM_DIR = $(PROJECT_DIR)/package/batocera/emulationstation/batocera-es-system
CONFIGGEN_DIR = $(PROJECT_DIR)/package/batocera/core/batocera-configgen

SYSTEMS_REPORT_VENV_SCRIPT = $(PROJECT_DIR)/.venv/bin/batocera-systems-report
SYSTEMS_REPORT_LAST_TARGET = $(lastword $(SYSTEMS_REPORT_TARGETS))
SYSTEMS_REPORT_DIR = $(OUTPUT_DIR)/systems-report
SYSTEMS_REPORT_DATADIR = $(SYSTEMS_REPORT_DIR)/data

SYSTEMS_REPORT_DIR_INITIALIZED = $(SYSTEMS_REPORT_DIR)/.stamp_initialized
SYSTEMS_REPORT_DATADIR_INITIALIZED = $(SYSTEMS_REPORT_DATADIR)/.stamp_initialized
SYSTEMS_REPORT_MK = $(SYSTEMS_REPORT_DIR)/.systems_report_targets.mk
SYSTEMS_REPORT_HTML = $(ES_SYSTEM_DIR)/batocera_systemsReport.html

.PHONY: systems-report-config
systems-report-config: $(SYSTEMS_REPORT_LAST_TARGET)-defconfig | $(DOCKER_IMAGE_AVAILABLE) $(DL_DIR_INITIALIZED) $(CCACHE_DIR_INITIALIZED) $(SYSTEMS_REPORT_DIR_INITIALIZED)
	@$(call MESSAGE,Generating buildroot makefile)

	$(call MAKE_BUILDROOT,systems-report) batocera-$(SYSTEMS_REPORT_LAST_TARGET)_defconfig

.PHONY: systems-report-data
systems-report-data: systems-report-config $(SYSTEMS_REPORT_DEFCONFIGS) | $(SYSTEMS_REPORT_DATADIR_INITIALIZED)
	@$(call MESSAGE,Generating systems report data)

	@# Remove data so buildroot can regenerate it
	@rm -rf '$(SYSTEMS_REPORT_DATADIR)'/*

	@printf '%s\n' 'SYSTEMS_REPORT_TARGETS := $(SYSTEMS_REPORT_TARGETS)' > '$(SYSTEMS_REPORT_MK)'

	$(call MAKE_BUILDROOT,systems-report) $(SYSTEMS_REPORT_MAKE_OPTS) systems-report-data

.PHONY: systems-report-data-clean
systems-report-data-clean:
	rm -rf $(SYSTEMS_REPORT_DATADIR)

.PHONY: systems-report-data-refresh
systems-report-data-refresh: systems-report-data-clean
	@$(MAKE) systems-report-data

.PHONY: _check_batocera_systems_report
_check_batocera_systems_report:
	$(call REQUIRE,$(SYSTEMS_REPORT_VENV_SCRIPT),Please run "uv sync" to install the virtual environment and dependencies)

.PHONY: systems-report
systems-report: _check_batocera_systems_report systems-report-data $(SYSTEMS_REPORT_HTML) | $(SYSTEMS_REPORT_DIR_INITIALIZED)
	@$(call MESSAGE,Generating systems report)

	$(SYSTEMS_REPORT_VENV_SCRIPT) $(if $(DIRECT_BUILD),,--buildroot-mapping=$(PROJECT_DIR):/build)\
		$(SYSTEMS_REPORT_DATADIR) \
		$(ES_SYSTEM_DIR)/es_systems.yml \
		$(ES_SYSTEM_DIR)/systems-explanations.yml \
		$(CONFIGGEN_DIR)/configs \
		$(SYSTEMS_REPORT_DIR)/batocera_systemsReport.json

	cp -f $(SYSTEMS_REPORT_HTML) $(SYSTEMS_REPORT_DIR)/batocera_systemsReport.html

.PHONY: systems-report-clean
systems-report-clean:
	rm -rf $(SYSTEMS_REPORT_DIR)

.PHONY: systems-report-refresh
systems-report-refresh: systems-report-clean
	@$(MAKE) systems-report

.PHONY: systems-report-serve
systems-report-serve: | $(SYSTEMS_REPORT_DIR_INITIALIZED)
	$(call REQUIRE,python3)
	$(if $(wildcard $(SYSTEMS_REPORT_DIR)/*),,$(error $* not built))
	@$(call MESSAGE,Serving systems report at $(call TERM_URL,http://localhost:8000/batocera_systemsReport.html))
	python3 -m http.server --directory $(SYSTEMS_REPORT_DIR)/
