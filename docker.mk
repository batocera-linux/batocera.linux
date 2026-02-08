DOCKER         ?= docker
DOCKER_OPTS    ?=
DOCKER_REPO    ?= batoceralinux
DOCKER_IMAGE_NAME   ?= batocera.linux-build

ifdef IMAGE_NAME
$(warning IMAGE_NAME will be removed in the future, please migrate to DOCKER_IMAGE_NAME)
DOCKER_IMAGE_NAME := $(IMAGE_NAME)
endif

DOCKER_IMAGE = $(DOCKER_REPO)/$(DOCKER_IMAGE_NAME)

ifndef BATCH_MODE
DOCKER_OPTS += -i
endif

ifdef DIRECT_BUILD
define RUN_DOCKER
	@$(error This is a direct build environment, cannot run Docker)
endef
else
UID  := $(shell id -u)
GID  := $(shell id -g)

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
		$(DOCKER_IMAGE)
endef
endif

.PHONY: _check_docker
_check_docker:
ifdef DIRECT_BUILD
	$(error This is a direct build environment)
endif
	$(call REQUIRE,$(DOCKER))

DOCKER_IMAGE_STAMP = $(PROJECT_DIR)/.ba-docker-image-available
DOCKER_IMAGE_AVAILABLE := $(if $(DIRECT_BUILD),,$(DOCKER_IMAGE_STAMP))

$(DOCKER_IMAGE_STAMP): DOCKER_ACTION ?= pull
$(DOCKER_IMAGE_STAMP): | _check_docker
	$(if $(filter build,$(DOCKER_ACTION)),\
		$(DOCKER) build -t $(DOCKER_IMAGE) .,\
		$(DOCKER) pull $(DOCKER_IMAGE))
	@touch $@

.PHONY: pull-docker-image
pull-docker-image: DOCKER_ACTION = pull
pull-docker-image: $(DOCKER_IMAGE_AVAILABLE)

.PHONY: build-docker-image
build-docker-image: DOCKER_ACTION = build
build-docker-image: $(DOCKER_IMAGE_AVAILABLE)

.PHONY: clean-for-docker-image
clean-for-docker-image:
	-@rm -f $(DOCKER_IMAGE_STAMP) >/dev/null

.PHONY: update-docker-image
update-docker-image: clean-for-docker-image
	@$(MAKE) pull-docker-image

.PHONY: rebuild-docker-image
rebuild-docker-image: clean-for-docker-image
	@$(MAKE) build-docker-image

.PHONY: publish-docker-image
publish-docker-image: | _check_docker
	@$(DOCKER) push $(DOCKER_IMAGE):latest
