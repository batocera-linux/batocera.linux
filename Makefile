PROJECT_DIR    := $(shell pwd)
DL_DIR         ?= $(PROJECT_DIR)/dl
OUTPUT_DIR     ?= $(PROJECT_DIR)/output
CCACHE_DIR     ?= $(PROJECT_DIR)/buildroot-ccache
LOCAL_MK       ?= $(PROJECT_DIR)/batocera.mk
EXTRA_OPTS     ?=
DOCKER_OPTS    ?=
NPROC          := $(shell nproc)
MAKE_JLEVEL    ?= $(NPROC)
MAKE_LLEVEL    ?= $(NPROC)
BATCH_MODE     ?=
PARALLEL_BUILD ?=
DIRECT_BUILD   ?=
DAYS           ?= 1
BR_DIR         := $(PROJECT_DIR)/buildroot

-include $(LOCAL_MK)

ifdef PARALLEL_BUILD
	EXTRA_OPTS +=  BR2_PER_PACKAGE_DIRECTORIES=y
	MAKE_OPTS  += -j$(MAKE_JLEVEL)
	MAKE_OPTS  += -l$(MAKE_LLEVEL)
endif

# List of packages that are always good to rebuild for versioning/stamps etc
MANDATORY_REBUILD_PKGS := batocera-es-system batocera-configgen batocera-system batocera-splash

# List of out-of-tree kernel modules that must be removed if the kernel is reset
# This list needs to be maintained if new modules are added or removed
KERNEL_MODULE_PKGS := rtl88x2bu rtl8852au rtl8852cu rtl8188eu rtl8192eu rtl8189fs rtl8821cu rtl8723bu rtl8812au guncon guncon3 hid-nx hid-tmff2 xpadneo xpad-noone nvidia nvidia470 nvidia580 r8125 rtw89 xone r8168 ayn-platform ayaneo-platform hid-t150 new-lg4ff ryzen-smu aic-8800 rwt88

# Across all batocera & buildroot packages find any updates and add to a list to rebuild
GIT_PACKAGES_TO_REBUILD := $(shell ( \
							  git log --since="$(DAYS) days ago" --name-only --format=%n -- $(PROJECT_DIR)/package/ \
							; cd $(BR_DIR) && git log --since="$(DAYS) days ago" --name-only --format=%n -- package/ \
						  ) \
						| grep -E '^package/' \
						| sed -r -e 's:package/batocera/(audio|boot|cases|controllers|core|database|emulationstation|emulators|firmwares|fonts|gpu|kodi|leds|libraries|looks|network|ports|screens|toolchain|utils|utils-host|wine)/([^/]+)/.*:\2:' \
						         -e 's:package/([^/]+)/.*:\1:' \
						| sort -u)

# Base list of all target packages to be reset
TARGET_PKGS_BASE := $(GIT_PACKAGES_TO_REBUILD) $(MANDATORY_REBUILD_PKGS)

# Check if a kernel package is present and conditionally add 'linux' and kernel modules
ifneq ($(filter linux linux-headers, $(TARGET_PKGS_BASE)),)
	TARGET_PKGS_BASE += linux
	KERNEL_MODULES_TO_RESET := $(KERNEL_MODULE_PKGS)
else
	KERNEL_MODULES_TO_RESET :=
endif

# Final list of all target packages to be reset (Base + Conditional Kernel Modules)
TARGET_PKGS := $(TARGET_PKGS_BASE) $(KERNEL_MODULES_TO_RESET)

# Cheats way, add 'host-' to each target package to ensure we are covered
HOST_PKGS_TO_RESET := $(foreach pkg,$(TARGET_PKGS),host-$(pkg))

# Final list is a combination of all target and host packages
PKGS_TO_RESET := $(sort $(TARGET_PKGS) $(HOST_PKGS_TO_RESET))

TARGETS := $(sort $(shell find $(PROJECT_DIR)/configs/ -name 'b*.board' | sed -n 's/.*\/batocera-\(.*\).board/\1/p'))
UID  := $(shell id -u)
GID  := $(shell id -g)
OS := $(shell uname)

ifeq ($(OS),Darwin)
$(if $(shell which gfind 2>/dev/null),,$(error "gfind not found! Please install findutils from Homebrew."))
FIND ?= gfind
else
FIND ?= find
endif

UC = $(shell echo '$1' | tr '[:lower:]' '[:upper:]')

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
	DOCKER         ?= docker

	ifndef BATCH_MODE
		DOCKER_OPTS += -i
	endif

	DOCKER_REPO    ?= batoceralinux
	IMAGE_NAME     ?= batocera.linux-build

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

vars:
	@echo "Supported targets:  $(TARGETS)"
	@echo "Project directory:  $(PROJECT_DIR)"
	@echo "Download directory: $(DL_DIR)"
	@echo "Build directory:    $(OUTPUT_DIR)"
	@echo "ccache directory:   $(CCACHE_DIR)"
	@echo "Extra options:      $(EXTRA_OPTS)"
ifndef DIRECT_BUILD
	@echo "Docker repo/image:  $(DOCKER_REPO)/$(IMAGE_NAME)"
	@echo "Docker options:     $(DOCKER_OPTS)"
endif
	@echo "Make options:       $(MAKE_OPTS)"

_check_docker:
	$(if $(DIRECT_BUILD),$(error "This is a direct build environment"))
	$(if $(shell which $(DOCKER) 2>/dev/null),, $(error "$(DOCKER) not found!"))

build-docker-image: _check_docker
	$(DOCKER) build . -t $(DOCKER_REPO)/$(IMAGE_NAME)
	@touch .ba-docker-image-available

.ba-docker-image-available:
	@$(MAKE) -s _check_docker
	@$(DOCKER) pull $(DOCKER_REPO)/$(IMAGE_NAME)
	@touch .ba-docker-image-available

batocera-docker-image: $(if $(DIRECT_BUILD),,.ba-docker-image-available)

update-docker-image: _check_docker
	-@rm .ba-docker-image-available > /dev/null
	@$(MAKE) -s batocera-docker-image

publish-docker-image: _check_docker
	@$(DOCKER) push $(DOCKER_REPO)/$(IMAGE_NAME):latest

output-dir-%: %-supported
	@mkdir -p $(OUTPUT_DIR)/$*

ccache-dir:
	@mkdir -p $(CCACHE_DIR)

dl-dir:
	@mkdir -p $(DL_DIR)

%-supported:
	$(if $(findstring $*, $(TARGETS)),,$(error "$* not supported!"))

%-clean: batocera-docker-image output-dir-%
	@$(MAKE_BUILDROOT) clean

%-config: batocera-docker-image output-dir-%
	@$(PROJECT_DIR)/configs/createDefconfig.sh $(PROJECT_DIR)/configs/batocera-$*
	@for opt in $(EXTRA_OPTS); do \
		echo $$opt >> $(PROJECT_DIR)/configs/batocera-$*_defconfig ; \
	done
	@$(MAKE_BUILDROOT) batocera-$*_defconfig

%-build: batocera-docker-image %-config ccache-dir dl-dir
	@$(MAKE_BUILDROOT) $(CMD)

%-source: batocera-docker-image %-config ccache-dir dl-dir
	@$(MAKE_BUILDROOT) source

%-show-build-order: batocera-docker-image %-config ccache-dir dl-dir
	@$(MAKE_BUILDROOT) show-build-order

%-kernel: batocera-docker-image %-config ccache-dir dl-dir
	@$(MAKE_BUILDROOT) linux-menuconfig

# force -j1 or graph-depends python script will bail
%-graph-depends: batocera-docker-image %-config ccache-dir dl-dir
	@$(MAKE_BUILDROOT) -j1 BR2_GRAPH_OUT=svg graph-depends

%-shell: batocera-docker-image output-dir-% _check_docker
	$(if $(BATCH_MODE),$(if $(CMD),,$(error "not supported in BATCH_MODE if CMD not specified!")),)
	@$(RUN_DOCKER) $(CMD)

%-ccache-stats: batocera-docker-image %-config ccache-dir dl-dir
	@$(MAKE_BUILDROOT) ccache-stats

%-build-cmd:
	@echo $(MAKE_BUILDROOT)

%-refresh: batocera-docker-image output-dir-%
	$(if $(PARALLEL_BUILD),,$(error "PARALLEL_BUILD=y must be set for %-refresh"))
	@echo "--- Refresh & Targeted Rebuild Trigger (DAYS=$(DAYS)) ---"

	@if [ -n "$(PKGS_TO_RESET)" ]; then \
		echo "Total packages to reset: $(PKGS_TO_RESET)"; \
		for pkg in $(PKGS_TO_RESET); do \
			echo "Surgically removing $$pkg from build and per-package directories..."; \
			rm -rf $(OUTPUT_DIR)/$*/build/$$pkg-*; \
			rm -rf $(OUTPUT_DIR)/$*/per-package/$$pkg; \
		done; \
	else \
		echo "No packages to reset."; \
	fi

	@echo "--- Removing Host and Target directories ---"
	rm -rf $(OUTPUT_DIR)/$*/host
	rm -rf $(OUTPUT_DIR)/$*/target
	rm -rf $(OUTPUT_DIR)/$*/target2
	
	@$(MAKE) $*-build

%-cleanbuild: %-clean %-build
	@echo

%-pkg:
	$(if $(PKG),,$(error "PKG not specified!"))

	@$(MAKE) $*-build CMD=$(PKG)

%-webserver: output-dir-%
	$(if $(wildcard $(OUTPUT_DIR)/$*/images/batocera/*),,$(error "$* not built!"))
	$(if $(shell which python3 2>/dev/null),,$(error "python3 not found!"))
ifeq ($(strip $(BOARD)),)
	$(if $(wildcard $(OUTPUT_DIR)/$*/images/batocera/images/$*/.*),,$(error "Directory not found: $(OUTPUT_DIR)/$*/images/batocera/images/$*"))
	python3 -m http.server --directory $(OUTPUT_DIR)/$*/images/batocera/images/$*/
else
	$(if $(wildcard $(OUTPUT_DIR)/$*/images/batocera/images/$(BOARD)/.*),,$(error "Directory not found: $(OUTPUT_DIR)/$*/images/batocera/images/$(BOARD)"))
	python3 -m http.server --directory $(OUTPUT_DIR)/$*/images/batocera/images/$(BOARD)/
endif

%-rsync: output-dir-%
	$(eval TMP := $(call UC, $*)_IP)
	$(if $(shell which rsync 2>/dev/null),, $(error "rsync not found!"))
	$(if $($(TMP)),,$(error "$(TMP) not set!"))
	rsync -e "ssh -o 'UserKnownHostsFile /dev/null' -o StrictHostKeyChecking=no" -av $(OUTPUT_DIR)/$*/target/ root@$($(TMP)):/

%-tail: output-dir-%
	@tail -F $(OUTPUT_DIR)/$*/build/build-time.log

%-snapshot: %-supported
	$(if $(shell which btrfs 2>/dev/null),, $(error "btrfs not found!"))
	@mkdir -p $(OUTPUT_DIR)/snapshots
	-@sudo btrfs sub del $(OUTPUT_DIR)/snapshots/$*-toolchain
	@btrfs subvolume snapshot -r $(OUTPUT_DIR)/$* $(OUTPUT_DIR)/snapshots/$*-toolchain

%-rollback: %-supported
	$(if $(shell which btrfs 2>/dev/null),, $(error "btrfs not found!"))
	-@sudo btrfs sub del $(OUTPUT_DIR)/$*
	@btrfs subvolume snapshot $(OUTPUT_DIR)/snapshots/$*-toolchain $(OUTPUT_DIR)/$*

%-flash: %-supported
	$(if $(DEV),,$(error "DEV not specified!"))
	@gzip -dc $(OUTPUT_DIR)/$*/images/batocera/images/$*/batocera-*.img.gz | sudo dd of=$(DEV) bs=5M status=progress
	@sync

%-upgrade: %-supported
	$(if $(DEV),,$(error "DEV not specified!"))
	-@sudo umount /tmp/mount
	-@mkdir -p /tmp/mount
	@sudo mount $(DEV)1 /tmp/mount
	@lsblk
	@ls /tmp/mount
	@echo "continue BATOCERA upgrade $(DEV)1 with $* build? [y/N]"
	@read line; if [ "$$line" != "y" ]; then echo aborting; exit 1 ; fi
	-@sudo rm /tmp/mount/boot/batocera
	@sudo tar xvf $(OUTPUT_DIR)/$*/images/batocera/images/$*/boot.tar.xz -C /tmp/mount --no-same-owner --exclude=batocera-boot.conf --exclude=config.txt
	@sudo umount /tmp/mount
	-@rmdir /tmp/mount
	@sudo fatlabel $(DEV)1 BATOCERA

%-toolchain: %-supported
	$(if $(shell which btrfs 2>/dev/null),, $(error "btrfs not found!"))
	-@sudo btrfs sub del $(OUTPUT_DIR)/$*
	@btrfs subvolume create $(OUTPUT_DIR)/$*
	@$(MAKE) $*-config
	@$(MAKE) $*-build CMD=toolchain
	@$(MAKE) $*-build CMD=llvm
	@$(MAKE) $*-snapshot

%-find-build-dups: %-supported
	@$(FIND) $(OUTPUT_DIR)/$*/build -maxdepth 1 -type d -printf '%T@ %p %f\n' | sed -r 's:\-[0-9a-f\.]+$$::' | sort -k3 -k1 | uniq -f 2 -d | cut -d' ' -f2

%-remove-build-dups: %-supported
	@while [ -n "`$(FIND) $(OUTPUT_DIR)/$*/build -maxdepth 1 -type d -printf '%T@ %p %f\n' | sed -r 's:\-[0-9a-f\.]+$$::' | sort -k3 -k1 | uniq -f 2 -d | cut -d' ' -f2 | grep .`" ]; do \
		$(FIND) $(OUTPUT_DIR)/$*/build -maxdepth 1 -type d -printf '%T@ %p %f\n' | sed -r 's:\-[0-9a-f\.]+$$::' | sort -k3 -k1 | uniq -f 2 -d | cut -d' ' -f2 | xargs rm -rf ; \
	done

find-dl-dups:
	@$(FIND) $(DL_DIR)/ -maxdepth 2 -type f -name "*.zip" -o -name "*.tar.*" -printf '%T@ %p %f\n' | sed -r 's:\-[-_0-9a-fvrgit\.]+(\.zip|\.tar\.[2a-z]+)$$::' | sort -k3 -k1 | uniq -f 2 -d | cut -d' ' -f2

remove-dl-dups:
	@while [ -n "`$(FIND) $(DL_DIR)/ -maxdepth 2 -type f -name "*.zip" -o -name "*.tar.*" -printf '%T@ %p %f\n' | sed -r 's:\-[-_0-9a-fvrgit\.]+(\.zip|\.tar\.[2a-z]+)$$::' | sort -k3 -k1 | uniq -f 2 -d | cut -d' ' -f2 | grep .`" ] ; do \
		$(FIND) $(DL_DIR) -maxdepth 2 -type f -name "*.zip" -o -name "*.tar.*" -printf '%T@ %p %f\n' | sed -r 's:\-[-_0-9a-fvrgit\.]+(\.zip|\.tar\.[2a-z]+)$$::' | sort -k3 -k1 | uniq -f 2 -d | cut -d' ' -f2 | xargs rm -rf ; \
	done

uart:
	$(if $(shell which picocom 2>/dev/null),, $(error "picocom not found!"))
	$(if $(SERIAL_DEV),,$(error "SERIAL_DEV not specified!"))
	$(if $(SERIAL_BAUDRATE),,$(error "SERIAL_BAUDRATE not specified!"))
	$(if $(wildcard $(SERIAL_DEV)),,$(error "$(SERIAL_DEV) not available!"))
	@picocom $(SERIAL_DEV) -b $(SERIAL_BAUDRATE)
