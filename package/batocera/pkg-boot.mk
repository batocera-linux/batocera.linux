define inner-boot-package

$(2)_INSTALL_IMAGES ?= YES
$(2)_BOOT_SRC ?=
$(2)_BINARIES_SUBDIR ?= $(1)

ifdef $(2)_BOOT_SRC
$(2)_SOURCE =
endif

ifndef $(2)_INSTALL_IMAGES_CMDS
define $(2)_INSTALL_IMAGES_CMDS
	$$(Q)mkdir -p $$(BINARIES_DIR)/$$($$(PKG)_BINARIES_SUBDIR)
	$$(Q)for pair in $$($$(PKG)_BOOT_SRC); do \
		src=$$$${pair%%:*}; \
		dst=$$$${pair#*:}; \
		cp $$($$(PKG)_PKGDIR)/$$$${src} $$(BINARIES_DIR)/$$($$(PKG)_BINARIES_SUBDIR)/$$$${dst} ; \
	done
endef
endif

# Call the generic package infrastructure to generate the necessary
# make targets
$(call inner-generic-package,$(1),$(2),$(2),target)

endef

boot-package = $(call inner-boot-package,$(pkgname),$(call UPPERCASE,$(pkgname)))
