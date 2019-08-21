################################################################################
#
# SSELPH_SCRAPER
#
################################################################################

#SSELPH_SCRAPER_VERSION = 1.4.6
SSELPH_SCRAPER_VERSION = 4737943b521b160a955f1c01c0d61d9967913ae7
SSELPH_SCRAPER_SITE = $(call github,sselph,scraper,$(SSELPH_SCRAPER_VERSION))

SSELPH_SCRAPER_DEPENDENCIES = host-go

SSELPH_SCRAPER_GOPATH = "$(@D)/Godeps/_workspace"
SSELPH_SCRAPER_MAKE_ENV = $(HOST_GO_TARGET_ENV) \
	CGO_ENABLED=1 \
	GOBIN="$(@D)/bin" \
	GOPATH="$(SSELPH_SCRAPER_GOPATH)" \
	PATH=$(BR_PATH)

SSELPH_SCRAPER_GOTAGS = cgo static_build

define SSELPH_SCRAPER_CONFIGURE_CMDS
	# github.com/kr/fs
	rm -rf $(SSELPH_SCRAPER_GOPATH)/src/github.com/kr
	mkdir -p $(SSELPH_SCRAPER_GOPATH)/src/github.com/kr
	cd $(SSELPH_SCRAPER_GOPATH)/src/github.com/kr && git clone https://github.com/kr/fs

	# github.com/mitchellh/go-homedir
	rm -rf $(SSELPH_SCRAPER_GOPATH)/src/github.com/mitchellh
	mkdir -p $(SSELPH_SCRAPER_GOPATH)/src/github.com/mitchellh
	cd $(SSELPH_SCRAPER_GOPATH)/src/github.com/mitchellh && git clone https://github.com/mitchellh/go-homedir

	# github.com/mitchellh/go-homedir
	rm -rf $(SSELPH_SCRAPER_GOPATH)/src/github.com/mitchellh
	mkdir -p $(SSELPH_SCRAPER_GOPATH)/src/github.com/mitchellh
	cd $(SSELPH_SCRAPER_GOPATH)/src/github.com/mitchellh && git clone https://github.com/mitchellh/go-homedir

	# github.com/nfnt/resize
	rm -rf $(SSELPH_SCRAPER_GOPATH)/src/github.com/nfnt
	mkdir -p $(SSELPH_SCRAPER_GOPATH)/src/github.com/nfnt
	cd $(SSELPH_SCRAPER_GOPATH)/src/github.com/nfnt && git clone https://github.com/nfnt/resize

	# github.com/hashicorp/golang-lru
	rm -rf $(SSELPH_SCRAPER_GOPATH)/src/github.com/hashicorp
	mkdir -p $(SSELPH_SCRAPER_GOPATH)/src/github.com/hashicorp
	cd $(SSELPH_SCRAPER_GOPATH)/src/github.com/hashicorp && git clone https://github.com/hashicorp/golang-lru

	# github.com/syndtr/goleveldb
	rm -rf $(SSELPH_SCRAPER_GOPATH)/src/github.com/syndtr
	mkdir -p $(SSELPH_SCRAPER_GOPATH)/src/github.com/syndtr
	cd $(SSELPH_SCRAPER_GOPATH)/src/github.com/syndtr && git clone https://github.com/syndtr/goleveldb

	# github.com/golang/snappy
	rm -rf $(SSELPH_SCRAPER_GOPATH)/src/github.com/golang
	mkdir -p $(SSELPH_SCRAPER_GOPATH)/src/github.com/golang
	cd $(SSELPH_SCRAPER_GOPATH)/src/github.com/golang && git clone https://github.com/golang/snappy

	# sselph-scraper
	mkdir -p $(SSELPH_SCRAPER_GOPATH)/src/github.com/sselph
	ln -sf $(@D) $(SSELPH_SCRAPER_GOPATH)/src/github.com/sselph/scraper
endef

define SSELPH_SCRAPER_BUILD_CMDS
	cd $(@D) && $(SSELPH_SCRAPER_MAKE_ENV) $(HOST_DIR)/usr/bin/go \
		build -v -o $(@D)/bin/sselph-scraper \
		-tags "$(SSELPH_SCRAPER_GOTAGS)" .
endef

define SSELPH_SCRAPER_INSTALL_TARGET_CMDS
	$(INSTALL) -D -m 0755 $(@D)/bin/sselph-scraper $(TARGET_DIR)/usr/bin/sselph-scraper
endef

$(eval $(generic-package))
