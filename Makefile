PROJECT_DIR := $(shell pwd)
DL_DIR      ?= $(PROJECT_DIR)/dl
OUTPUT_DIR  ?= $(PROJECT_DIR)/output
CCACHE_DIR  ?= $(PROJECT_DIR)/buildroot-ccache
LOCAL_MK	?= $(PROJECT_DIR)/batocera.mk
EXTRA_PKGS  ?=

-include $(LOCAL_MK)

DOCKER_REPO := batocera
IMAGE_NAME  := batocera.linux-build

TARGETS := $(sort $(shell find $(PROJECT_DIR)/configs/ -name 'b*' | sed -n 's/.*\/batocera-\(.*\)_defconfig/\1/p'))
UID  := $(shell id -u)
GID  := $(shell id -g)
USER := $(shell whoami)

ifeq (, $(shell which docker 2>/dev/null))
$(error "docker not found!")
endif

vars:
	@echo "Supported targets:     $(TARGETS)"
	@echo "Project directory:     $(PROJECT_DIR)"
	@echo "Download directory:    $(DL_DIR)"
	@echo "Build directory:       $(OUTPUT_DIR)"
	@echo "ccache directory:      $(CCACHE_DIR)"

build-docker-image:
	docker build . -t $(DOCKER_REPO)/$(IMAGE_NAME)
	@touch .ba-docker-image-available

.ba-docker-image-available:
	@docker pull $(DOCKER_REPO)/$(IMAGE_NAME)
	@touch .ba-docker-image-available

batocera-docker-image: .ba-docker-image-available

update-docker-image:
	-@rm .ba-docker-image-available > /dev/null
	@$(MAKE) download-docker-image

publish-docker-image:
	@docker push $(DOCKER_REPO)/$(IMAGE_NAME):latest

output-dir-%:
	@mkdir -p $(OUTPUT_DIR)/$*

ccache-dir:
	@mkdir -p $(CCACHE_DIR)

%-supported:
	$(if $(findstring $*, $(TARGETS)),,$(error "$* not supported!"))

%-clean: batocera-docker-image %-supported output-dir-%
	@docker run -it --init --rm \
		-v $(PROJECT_DIR):/build \
		-v $(DL_DIR):/build/buildroot/dl \
		-v $(OUTPUT_DIR)/$*:/$* \
		-v /etc/passwd:/etc/passwd:ro \
		-v /etc/group:/etc/group:ro \
		-u $(UID):$(GID) \
		batocera/batocera.linux-build \
		make O=/$* BR2_EXTERNAL=/build -C /build/buildroot clean

%-config: batocera-docker-image %-supported output-dir-%
	@cp -f $(PROJECT_DIR)/configs/batocera-$*_defconfig $(PROJECT_DIR)/configs/batocera-$*_defconfig-tmp
	@for opt in $(EXTRA_OPTS); do \
		echo $$opt >> $(PROJECT_DIR)/configs/batocera-$*_defconfig ; \
	done
	@docker run -it --init --rm \
		-v $(PROJECT_DIR):/build \
		-v $(DL_DIR):/build/buildroot/dl \
		-v $(OUTPUT_DIR)/$*:/$* \
		-v /etc/passwd:/etc/passwd:ro \
		-v /etc/group:/etc/group:ro \
		-u $(UID):$(GID) \
		batocera/batocera.linux-build \
		make O=/$* BR2_EXTERNAL=/build -C /build/buildroot batocera-$*_defconfig
	@mv -f $(PROJECT_DIR)/configs/batocera-$*_defconfig-tmp $(PROJECT_DIR)/configs/batocera-$*_defconfig

%-build: batocera-docker-image %-supported %-config ccache-dir
	@docker run -it --rm \
		-v $(PROJECT_DIR):/build \
		-v $(DL_DIR):/build/buildroot/dl \
		-v $(OUTPUT_DIR)/$*:/$* \
		-v $(CCACHE_DIR):/home/$(USER)/.buildroot-ccache \
		-u $(UID):$(GID) \
		-v /etc/passwd:/etc/passwd:ro \
		-v /etc/group:/etc/group:ro \
		batocera/batocera.linux-build \
		make O=/$* BR2_EXTERNAL=/build -C /build/buildroot $(CMD)

%-shell: batocera-docker-image %-supported output-dir-%
	@docker run -it --rm \
		-v $(PROJECT_DIR):/build \
		-v $(DL_DIR):/build/buildroot/dl \
		-v $(OUTPUT_DIR)/$*:/$* -w /$* \
		-v $(CCACHE_DIR):/home/$(USER)/.buildroot-ccache \
		-u $(UID):$(GID) \
		-v /etc/passwd:/etc/passwd:ro \
		-v /etc/group:/etc/group:ro \
		batocera/batocera.linux-build

%-cleanbuild: %-clean %-build
	

%-pkg:
	$(if $(PKG),,$(error "PKG not specified!"))
	@$(MAKE) $*-build CMD=$(PKG)
