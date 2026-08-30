################################################################################
# inner-local-python-package -- defines how the installation of a local python
# package should be done using the python package infrastructure to generate the
# necessary make targets
#
#  argument 1 is the lowercase package name
#  argument 2 is the uppercase package name, including a HOST_ prefix
#             for host packages
#  argument 3 is the uppercase package name, without the HOST_ prefix
#             for host packages
#  argument 4 is the type (target or host)
################################################################################
define inner-local-python-package
$(2)_SOURCE =
$(2)_OVERRIDE_SRCDIR ?= $$($(2)_PKGDIR)
$(2)_OVERRIDE_SRCDIR_RSYNC_EXCLUSIONS ?= --exclude=".*" --exclude="**/__pycache__/" \
					 --exclude="dist" --exclude="*.mk" --exclude="Config.in" \
					 --exclude="**/py.typed" --exclude="tests"

$(call inner-python-package,$(1),$(2),$(3),$(4))
endef

local-python-package = $(call inner-local-python-package,$(pkgname),$(call UPPERCASE,$(pkgname)),$(call UPPERCASE,$(pkgname)),target)
host-local-python-package = $(call inner-local-python-package,host-$(pkgname),$(call UPPERCASE,host-$(pkgname)),$(call UPPERCASE,$(pkgname)),host)
