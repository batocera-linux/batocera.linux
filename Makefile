PROJECT_DIR    := $(shell pwd)
DL_DIR         ?= $(PROJECT_DIR)/dl
OUTPUT_DIR     ?= $(PROJECT_DIR)/output
CCACHE_DIR     ?= $(PROJECT_DIR)/buildroot-ccache
LOCAL_MK	   ?= $(PROJECT_DIR)/batocera.mk
EXTRA_PKGS	   ?=
DOCKER_OPTS    ?=
MAKE_JLEVEL    ?= $(shell nproc)
BATCH_MODE     ?=
PARALLEL_BUILD ?=

-include $(LOCAL_MK)

ifdef PARALLEL_BUILD
	EXTRA_OPTS +=  BR2_PER_PACKAGE_DIRECTORIES=y
	MAKE_OPTS  += -j$(MAKE_JLEVEL)
endif

ifndef BATCH_MODE
	DOCKER_OPTS += -i
endif

DOCKER_REPO := batoceralinux
IMAGE_NAME  := batocera.linux-build

TARGETS := $(sort $(shell find $(PROJECT_DIR)/configs/ -name 'b*' | sed -n 's/.*\/batocera-\(.*\)_defconfig/\1/p'))
UID  := $(shell id -u)
GID  := $(shell id -g)

$(if $(shell which docker 2>/dev/null),, $(error "docker not found!"))

UC = $(shell echo '$1' | tr '[:lower:]' '[:upper:]')

vars:
	@echo "Supported targets:  $(TARGETS)"
	@echo "Project directory:  $(PROJECT_DIR)"
	@echo "Download directory: $(DL_DIR)"
	@echo "Build directory:    $(OUTPUT_DIR)"
	@echo "ccache directory:   $(CCACHE_DIR)"
	@echo "Extra options:      $(EXTRA_OPTS)"
	@echo "Docker options:     $(DOCKER_OPTS)"
	@echo "Make options:       $(MAKE_OPTS)"


build-docker-image:
	docker build . -t $(DOCKER_REPO)/$(IMAGE_NAME)
	@touch .ba-docker-image-available

.ba-docker-image-available:
	@docker pull $(DOCKER_REPO)/$(IMAGE_NAME)
	@touch .ba-docker-image-available

batocera-docker-image: .ba-docker-image-available

update-docker-image:
	-@rm .ba-docker-image-available > /dev/null
	@$(MAKE) batocera-docker-image

publish-docker-image:
	@docker push $(DOCKER_REPO)/$(IMAGE_NAME):latest

output-dir-%: %-supported
	@mkdir -p $(OUTPUT_DIR)/$*

ccache-dir:
	@mkdir -p $(CCACHE_DIR)

dl-dir:
	@mkdir -p $(DL_DIR)

%-supported:
	$(if $(findstring $*, $(TARGETS)),,$(error "$* not supported!"))

%-clean: batocera-docker-image output-dir-%
	@docker run -t --init --rm \
		-v $(PROJECT_DIR):/build \
		-v $(DL_DIR):/build/buildroot/dl \
		-v $(OUTPUT_DIR)/$*:/$* \
		-v /etc/passwd:/etc/passwd:ro \
		-v /etc/group:/etc/group:ro \
		-u $(UID):$(GID) \
		$(DOCKER_OPTS) \
		$(DOCKER_REPO)/$(IMAGE_NAME) \
		make O=/$* BR2_EXTERNAL=/build -C /build/buildroot clean

%-config: batocera-docker-image output-dir-%
	@cp -f $(PROJECT_DIR)/configs/batocera-$*_defconfig $(PROJECT_DIR)/configs/batocera-$*_defconfig-tmp
	@for opt in $(EXTRA_OPTS); do \
		echo $$opt >> $(PROJECT_DIR)/configs/batocera-$*_defconfig ; \
	done
	@docker run -t --init --rm \
		-v $(PROJECT_DIR):/build \
		-v $(DL_DIR):/build/buildroot/dl \
		-v $(OUTPUT_DIR)/$*:/$* \
		-v /etc/passwd:/etc/passwd:ro \
		-v /etc/group:/etc/group:ro \
		-u $(UID):$(GID) \
		$(DOCKER_OPTS) \
		$(DOCKER_REPO)/$(IMAGE_NAME) \
		make O=/$* BR2_EXTERNAL=/build -C /build/buildroot batocera-$*_defconfig
	@mv -f $(PROJECT_DIR)/configs/batocera-$*_defconfig-tmp $(PROJECT_DIR)/configs/batocera-$*_defconfig

%-build: batocera-docker-image %-config ccache-dir dl-dir
	@docker run -t --init --rm \
		-v $(PROJECT_DIR):/build \
		-v $(DL_DIR):/build/buildroot/dl \
		-v $(OUTPUT_DIR)/$*:/$* \
		-v $(CCACHE_DIR):$(HOME)/.buildroot-ccache \
		-u $(UID):$(GID) \
		-v /etc/passwd:/etc/passwd:ro \
		-v /etc/group:/etc/group:ro \
		$(DOCKER_OPTS) \
		$(DOCKER_REPO)/$(IMAGE_NAME) \
		make $(MAKE_OPTS) O=/$* BR2_EXTERNAL=/build -C /build/buildroot $(CMD)

%-source: batocera-docker-image %-config ccache-dir dl-dir
	@docker run -t --init --rm \
		-v $(PROJECT_DIR):/build \
		-v $(DL_DIR):/build/buildroot/dl \
		-v $(OUTPUT_DIR)/$*:/$* \
		-v $(CCACHE_DIR):$(HOME)/.buildroot-ccache \
		-u $(UID):$(GID) \
		-v /etc/passwd:/etc/passwd:ro \
		-v /etc/group:/etc/group:ro \
		$(DOCKER_OPTS) \
		$(DOCKER_REPO)/$(IMAGE_NAME) \
		make $(MAKE_OPTS) O=/$* BR2_EXTERNAL=/build -C /build/buildroot source

%-kernel: batocera-docker-image %-config ccache-dir dl-dir
	@docker run -t --init --rm \
		-v $(PROJECT_DIR):/build \
		-v $(DL_DIR):/build/buildroot/dl \
		-v $(OUTPUT_DIR)/$*:/$* \
		-v $(CCACHE_DIR):$(HOME)/.buildroot-ccache \
		-u $(UID):$(GID) \
		-v /etc/passwd:/etc/passwd:ro \
		-v /etc/group:/etc/group:ro \
		$(DOCKER_OPTS) \
		$(DOCKER_REPO)/$(IMAGE_NAME) \
		make $(MAKE_OPTS) O=/$* BR2_EXTERNAL=/build -C /build/buildroot linux-menuconfig

%-graph-depends: batocera-docker-image %-config ccache-dir dl-dir
	@docker run -it --init --rm \
		-v $(PROJECT_DIR):/build \
		-v $(DL_DIR):/build/buildroot/dl \
		-v $(OUTPUT_DIR)/$*:/$* \
		-v $(CCACHE_DIR):$(HOME)/.buildroot-ccache \
		-u $(UID):$(GID) \
		-v /etc/passwd:/etc/passwd:ro \
		-v /etc/group:/etc/group:ro \
		$(DOCKER_OPTS) \
		$(DOCKER_REPO)/$(IMAGE_NAME) \
		make O=/$* BR2_EXTERNAL=/build BR2_GRAPH_OUT=svg -C /build/buildroot graph-depends

%-shell: batocera-docker-image output-dir-%
	$(if $(BATCH_MODE),$(error "not suppoorted in BATCH_MODE!"),)
	@docker run -t --init --rm \
		-v $(PROJECT_DIR):/build \
		-v $(DL_DIR):/build/buildroot/dl \
		-v $(OUTPUT_DIR)/$*:/$* \
		-w /$* \
		-v $(CCACHE_DIR):$(HOME)/.buildroot-ccache \
		-u $(UID):$(GID) \
		$(DOCKER_OPTS) \
		-v /etc/passwd:/etc/passwd:ro \
		-v /etc/group:/etc/group:ro \
		$(DOCKER_REPO)/$(IMAGE_NAME)

%-cleanbuild: %-clean %-build
	@echo

%-pkg:
	$(if $(PKG),,$(error "PKG not specified!"))
	@$(MAKE) $*-build CMD=$(PKG)

%-webserver: output-dir-%
	$(if $(wildcard $(OUTPUT_DIR)/$*/images/batocera/*),,$(error "$* not built!"))
	$(if $(shell which python 2>/dev/null),,$(error "python not found!"))
	@python3 -m http.server --directory $(OUTPUT_DIR)/$*/images/batocera/images/$*/

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
	@gzip -dc $(OUTPUT_DIR)/$*/images/batocera/images/batocera-*.img.gz | sudo dd of=$(DEV) bs=5M status=progress
	@sync

%-upgrade: %-supported
	$(if $(DEV),,$(error "DEV not specified!"))
	-@sudo umount /tmp/mount
	-@mkdir /tmp/mount
	@sudo mount $(DEV)1 /tmp/mount
	-@sudo rm /tmp/mount/boot/batocera
	@sudo tar xvf $(OUTPUT_DIR)/$*/images/batocera/boot.tar.xz -C /tmp/mount --no-same-owner
	@sudo umount /tmp/mount
	-@rmdir /tmp/mount

%-toolchain: %-supported
	$(if $(shell which btrfs 2>/dev/null),, $(error "btrfs not found!"))
	-@sudo btrfs sub del $(OUTPUT_DIR)/$*
	@btrfs subvolume create $(OUTPUT_DIR)/$*
	@$(MAKE) $*-config
	@$(MAKE) $*-build CMD=toolchain
	@$(MAKE) $*-build CMD=llvm
	@$(MAKE) $*-snapshot

uart:
	$(if $(shell which picocom 2>/dev/null),, $(error "picocom not found!"))
	$(if $(SERIAL_DEV),,$(error "SERIAL_DEV not specified!"))
	$(if $(SERIAL_BAUDRATE),,$(error "SERIAL_BAUDRATE not specified!"))
	$(if $(wildcard $(SERIAL_DEV)),,$(error "$(SERIAL_DEV) not available!"))
	@picocom $(SERIAL_DEV) -b $(SERIAL_BAUDRATE)
