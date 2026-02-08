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
DOCKER_OPTS    ?=
MAKE_JLEVEL    ?= $(NPROC)
MAKE_LLEVEL    ?= $(NPROC)
BATCH_MODE     ?=
PARALLEL_BUILD ?=
DIRECT_BUILD   ?=
DAYS           ?= 1
SYSTEMS_REPORT_EXCLUDE_TARGETS ?= odin

USER_DEFCONFIG := $(PROJECT_DIR)/configs/.user_defconfig

# Macro to append a line to the user defconfig file
define add-defconfig
$(file >>$(USER_DEFCONFIG),$(1))
endef

# Clear the user defconfig file at the start before including
# the user's makefile customizations
$(file >$(USER_DEFCONFIG),)

-include $(LOCAL_MK)

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

# List of packages that are always good to rebuild for versioning/stamps etc
MANDATORY_REBUILD_PKGS := batocera-es-system batocera-configgen batocera-system batocera-splash

# Lazily evaluated variable to avoid re-evaluation on each use
# VAR = $(eval VAR := ...)$(VAR)

# List of out-of-tree kernel modules that must be removed if the kernel is reset
# This list needs to be maintained if new modules are added or removed
KERNEL_MODULE_PKGS = $(eval KERNEL_MODULE_PKGS := $(sort $(patsubst %.mk,%,$(notdir $(shell grep -rl '\$$(eval \$$(kernel-module))' $(PROJECT_DIR)/package 2>/dev/null)))))$(KERNEL_MODULE_PKGS)

# Across all batocera & buildroot packages find any updates and add to a list to rebuild
GIT_PACKAGES_TO_REBUILD = $(eval GIT_PACKAGES_TO_REBUILD := $(shell \
	{ git -C $(PROJECT_DIR) log --since="$(DAYS) days ago" --name-only --format=%n -- package/ ; \
	  git -C $(PROJECT_DIR)/buildroot log --since="$(DAYS) days ago" --name-only --format=%n -- package/ ; } \
	| sed -r 's:^package/::; /^batocera\/[^/]*$$/d; s:^batocera/[^/]+/::; s:^([^/]+)/.*:\1:' \
	| sort -u))$(GIT_PACKAGES_TO_REBUILD)

# Base list of all target packages to be reset
TARGET_PKGS_BASE = $(GIT_PACKAGES_TO_REBUILD) $(MANDATORY_REBUILD_PKGS)

# Check if a kernel package is present and conditionally add 'linux' and kernel modules
KERNEL_MODULES_TO_RESET = $(if $(filter linux linux-headers,$(TARGET_PKGS_BASE)),linux $(KERNEL_MODULE_PKGS))

# Final list of all target packages to be reset (Base + Conditional Kernel Modules)
TARGET_PKGS = $(TARGET_PKGS_BASE) $(KERNEL_MODULES_TO_RESET)

# Cheats way, add 'host-' to each target package to ensure we are covered
HOST_PKGS_TO_RESET = $(addprefix host-,$(TARGET_PKGS))

# Final list is a combination of all target and host packages
PKGS_TO_RESET = $(sort $(TARGET_PKGS) $(HOST_PKGS_TO_RESET))

# All supported targets based on the board files in configs/, sorted for consistency
TARGETS := $(sort $(patsubst batocera-%.board,%,$(notdir $(wildcard $(PROJECT_DIR)/configs/*.board))))

# All supported targets for systems report generation
SYSTEMS_REPORT_TARGETS := $(filter-out $(SYSTEMS_REPORT_EXCLUDE_TARGETS) x86_wow64,$(TARGETS))

# All defconfig files for systems report targets, generated from the board files
SYSTEMS_REPORT_DEFCONFIGS = $(foreach target,$(SYSTEMS_REPORT_TARGETS),$(call target-defconfig,$(target)))

## BEGIN helper macros

REQUIRE = $(if $(shell command -v $(1) 2>/dev/null),,$(error $(1) not found$(if $(2),; $(2))))
UC = $(shell echo '$1' | tr '[:lower:]' '[:upper:]')

# END helper macros

# define build command based on whether we are building direct or inside a docker build container
ifdef DIRECT_BUILD

define MAKE_BUILDROOT
	make $(MAKE_OPTS) O=$(OUTPUT_DIR)/$* \
		BR2_EXTERNAL=$(PROJECT_DIR) \
		BR2_DL_DIR=$(DL_DIR) \
		BR2_CCACHE_DIR=$(CCACHE_DIR) \
		-C $(PROJECT_DIR)/buildroot
endef

else # DIRECT_BUILD

UID  := $(shell id -u)
GID  := $(shell id -g)

DOCKER ?= docker

ifndef BATCH_MODE
DOCKER_OPTS += -i
endif

DOCKER_REPO ?= batoceralinux
IMAGE_NAME ?= batocera.linux-build

define RUN_DOCKER
	$(DOCKER) run -t --init --rm \
		-e HOME \
		-v $(PROJECT_DIR):/build \
		-v $(DL_DIR):/build/buildroot/dl \
		-v $(OUTPUT_DIR)/$*:/$* \
		-v $(CCACHE_DIR):$(HOME)/.buildroot-ccache \
		-w /$* \
		-v /etc/passwd:/etc/passwd:ro \
		-v /etc/group:/etc/group:ro \
		-u $(UID):$(GID) \
		$(DOCKER_OPTS) \
		$(DOCKER_REPO)/$(IMAGE_NAME)
endef

define MAKE_BUILDROOT
	$(RUN_DOCKER) make $(MAKE_OPTS) O=/$* \
			BR2_EXTERNAL=/build \
			-C /build/buildroot
endef

endif # DIRECT_BUILD

.PHONY: vars
vars:
	@echo "Supported targets:  $(TARGETS)"
	@echo "Project directory:  $(PROJECT_DIR)"
	@echo "Download directory: $(DL_DIR)"
	@echo "Build directory:    $(OUTPUT_DIR)"
	@echo "ccache directory:   $(CCACHE_DIR)"
	@echo "Extra defconfig:"
	@sed -e '/^\s*$$/d' -e 's/^/  /' "$(USER_DEFCONFIG)"
ifndef DIRECT_BUILD
	@echo "Docker repo/image:  $(DOCKER_REPO)/$(IMAGE_NAME)"
	@echo "Docker options:     $(DOCKER_OPTS)"
endif
	@echo "Make options:       $(MAKE_OPTS)"

.PHONY: _check_docker
_check_docker:
ifdef DIRECT_BUILD
	$(error This is a direct build environment)
endif
	$(call REQUIRE,$(DOCKER))

.PHONY: _check_find
_check_find:
ifeq ($(OS),Darwin)
	$(call REQUIRE,gfind,Please install findutils from Homebrew)
endif

.PHONY: build-docker-image
build-docker-image: _check_docker
	$(DOCKER) build . -t $(DOCKER_REPO)/$(IMAGE_NAME)
	@touch .ba-docker-image-available

.ba-docker-image-available:
	@$(MAKE) -s _check_docker
	@$(DOCKER) pull $(DOCKER_REPO)/$(IMAGE_NAME)
	@touch .ba-docker-image-available

.PHONY: batocera-docker-image
batocera-docker-image: $(if $(DIRECT_BUILD),,.ba-docker-image-available)

.PHONY: update-docker-image
update-docker-image: _check_docker
	-@rm .ba-docker-image-available > /dev/null
	@$(MAKE) -s batocera-docker-image

.PHONY: publish-docker-image
publish-docker-image: _check_docker
	@$(DOCKER) push $(DOCKER_REPO)/$(IMAGE_NAME):latest

# Target macros for files or directories (actual files)
target-output-dir = $(OUTPUT_DIR)/$(1)
target-board-file = $(PROJECT_DIR)/configs/batocera-$(1).board
target-defconfig = $(PROJECT_DIR)/configs/batocera-$(1)_defconfig
target-systems-report-dir = $(OUTPUT_DIR)/$(1)/systems-report
target-systems-report-mk = $(call target-output-dir,$(1))/.systems_report_targets.mk

# File patterns for generated files based on target macros
TARGET_OUTPUT_DIR_PATTERN = $(call target-output-dir,%)
TARGET_BOARD_FILE_PATTERN = $(call target-board-file,%)
TARGET_DEFCONFIG_PATTERN = $(call target-defconfig,%)

# Macros for getting the $* equivalent file or directory
TARGET_OUTPUT_DIR = $(call target-output-dir,$*)
TARGET_BOARD_FILE = $(call target-board-file,$*)
TARGET_DEFCONFIG = $(call target-defconfig,$*)
TARGET_SYSTEMS_REPORT_DIR = $(call target-systems-report-dir,$*)
TARGET_SYSTEMS_REPORT_MK = $(call target-systems-report-mk,$*)

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

%-clean: | batocera-docker-image $(DL_DIR_INITIALIZED) $(CCACHE_DIR_INITIALIZED) $(TARGET_OUTPUT_DIR_INITIALIZED)
	@$(MAKE_BUILDROOT) clean
	@if [ -f '$(TARGET_DEFCONFIG)' ]; then \
		echo "Removing config for $*..."; \
		rm -f '$(TARGET_DEFCONFIG)'; \
	fi

%-defconfig: $(TARGET_DEFCONFIG_PATTERN) | %-supported
	@:

%-config: %-defconfig | batocera-docker-image $(DL_DIR_INITIALIZED) $(CCACHE_DIR_INITIALIZED) $(TARGET_OUTPUT_DIR_INITIALIZED)
	@$(MAKE_BUILDROOT) batocera-$*_defconfig

%-build: %-config
	@$(MAKE_BUILDROOT) $(CMD)

%-source: %-config
	@$(MAKE_BUILDROOT) source

%-show-build-order: %-config
	@$(MAKE_BUILDROOT) show-build-order

%-kernel: %-config
	@$(MAKE_BUILDROOT) linux-menuconfig

# force -j1 or graph-depends python script will bail
%-graph-depends: %-config
	@$(MAKE_BUILDROOT) -j1 BR2_GRAPH_OUT=svg graph-depends

%-shell: %-config
ifdef BATCH_MODE
	$(if $(CMD),,$(error CMD is required to use $*-shell in BATCH_MODE))
endif
	@$(RUN_DOCKER) $(CMD)

%-ccache-stats: %-config
	@$(MAKE_BUILDROOT) ccache-stats

%-build-cmd: %-supported
	@echo $(MAKE_BUILDROOT)

%-refresh: | batocera-docker-image $(TARGET_OUTPUT_DIR_INITIALIZED)
ifndef PARALLEL_BUILD
	$(error PARALLEL_BUILD=y must be set for $*-refresh)
endif
	@echo "--- Refresh & Targeted Rebuild Trigger (DAYS=$(DAYS)) ---"

	@if [ -n "$(PKGS_TO_RESET)" ]; then \
		echo "Total packages to reset: $(PKGS_TO_RESET)"; \
		for pkg in $(PKGS_TO_RESET); do \
			echo "Surgically removing $$pkg from build and per-package directories..."; \
			rm -rf $(TARGET_OUTPUT_DIR)/build/$$pkg-*; \
			rm -rf $(TARGET_OUTPUT_DIR)/per-package/$$pkg; \
		done; \
	else \
		echo "No packages to reset."; \
	fi

	@echo "--- Removing Host and Target directories ---"
	@for dir in include share lib/pkgconfig; do \
		if [ -d "$(TARGET_OUTPUT_DIR)/host/$$dir" ]; then \
			echo "Cleaning host staging: $$dir..."; \
			rm -rf $(TARGET_OUTPUT_DIR)/host/$$dir; \
		fi; \
	done
	rm -rf $(TARGET_OUTPUT_DIR)/target
	rm -rf $(TARGET_OUTPUT_DIR)/target2

	@$(MAKE) $*-build

%-cleanbuild: %-clean
	$(MAKE) $*-build

%-pkg: %-supported
	$(if $(PKG),,$(error PKG not specified))

	@$(MAKE) $*-build CMD=$(PKG)

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
	@$(MAKE_BUILDROOT) update-po-files

%-systems-report-clean: %-supported
	-@rm -rf $(TARGET_SYSTEMS_REPORT_DIR)

%-systems-report: $(SYSTEMS_REPORT_DEFCONFIGS) %-config
	@echo "SYSTEMS_REPORT_TARGETS := $(SYSTEMS_REPORT_TARGETS)" > "$(TARGET_SYSTEMS_REPORT_MK)"
	@$(MAKE_BUILDROOT) systems-report

%-systems-report-serve: | $(TARGET_OUTPUT_DIR_INITIALIZED)
	$(call REQUIRE,python3)
	$(if $(wildcard $(TARGET_SYSTEMS_REPORT_DIR)/*),,$(error $* not built))
	python3 -m http.server --directory $(TARGET_SYSTEMS_REPORT_DIR)/
