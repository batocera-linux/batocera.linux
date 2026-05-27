################################################################################
# inner-boot-package -- defines how the installation of a boot package should
# be done, implements a default installation procedure for boot packages and
# calls the generic package infrastructure to generate the necessary make targets
#
#  argument 1 is the lowercase package name
#  argument 2 is the uppercase package name
################################################################################
define inner-boot-package

$(2)_INSTALL_IMAGES ?= YES
$(2)_BOOT_SRC ?=
$(2)_BOOT_SRC_DIR ?=
$(2)_BINARIES_SUBDIR ?= $(1)

ifdef $(2)_BOOT_SRC
ifndef $(2)_SITE
$(2)_SOURCE =
endif
endif

ifndef $(2)_INSTALL_IMAGES_CMDS
define $(2)_INSTALL_IMAGES_CMDS
	$$(Q)mkdir -p $$(BINARIES_DIR)/$$($$(PKG)_BINARIES_SUBDIR)
	$$(Q)for pair in $$($$(PKG)_BOOT_SRC); do \
		src=$$$${pair%%:*}; \
		dst=$$$${pair#*:}; \
		cp $$($$(PKG)_BOOT_SRC_DIR)/$$$${src} $$(BINARIES_DIR)/$$($$(PKG)_BINARIES_SUBDIR)/$$$${dst} ; \
	done
endef
endif

# Call the generic package infrastructure to generate the necessary
# make targets
$(call inner-generic-package,$(1),$(2),$(2),target)

ifndef $(2)_BOOT_SRC_DIR
ifdef $(2)_SOURCE
$(2)_BOOT_SRC_DIR = $($(2)_BUILDDIR)
else
$(2)_BOOT_SRC_DIR = $($(2)_PKGDIR)
endif
endif

endef

################################################################################
# boot-package -- the target generator macro for boot packages
################################################################################

boot-package = $(call inner-boot-package,$(pkgname),$(call UPPERCASE,$(pkgname)))
