EMULATOR_INFO_PACKAGES :=
EMULATOR_INFO_PACKAGES_ALL :=
EMULATOR_INFO_PATHS :=
EMULATOR_INFO_PATHS_ALL :=

define inner-emulator-info-package
# Register functions weren't used to set up $(2)_EMULATOR_INFO
ifndef $(2)_EMULATOR_INFO_ALL
$(2)_EMULATOR_INFO_ALL := $$($(2)_EMULATOR_INFO)
endif

$(2)_EMULATOR_INFO_PATHS = $$(addprefix $(pkgdir)/,$$($(2)_EMULATOR_INFO))
$(2)_EMULATOR_INFO_PATHS_ALL = $$(addprefix $(pkgdir)/,$$($(2)_EMULATOR_INFO_ALL))

ifeq ($$($$($(2)_KCONFIG_VAR)),y)
EMULATOR_INFO_PACKAGES += $(1)
EMULATOR_INFO_PATHS += $$($(2)_EMULATOR_INFO_PATHS)
endif

EMULATOR_INFO_PACKAGES_ALL += $(1)
EMULATOR_INFO_PATHS_ALL += $$($(2)_EMULATOR_INFO_PATHS_ALL)
endef

emulator-info-package = $(call inner-emulator-info-package,$(pkgname),$(call UPPERCASE,$(pkgname)))

define __inner-register
$(1)_EMULATOR_INFO += $(2)
$(1)_EMULATOR_INFO_ALL += $(2)
endef

define __inner-register-ifeq
ifeq ($(2),$(3))
$(1)_EMULATOR_INFO += $(4)
endif
$(1)_EMULATOR_INFO_ALL += $(4)
endef

define __inner-register-ifneq
ifneq ($(2),$(3))
$(1)_EMULATOR_INFO += $(4)
endif
$(1)_EMULATOR_INFO_ALL += $(4)
endef

define register
$(call __inner-register,$(call UPPERCASE,$(pkgname)),$(1))
endef

define register-ifeq
$(call __inner-register-ifeq,$(call UPPERCASE,$(pkgname)),$(1),$(2),$(3))
endef

define register-ifneq
$(call __inner-register-ifneq,$(call UPPERCASE,$(pkgname)),$(1),$(2),$(3))
endef

define register-if-one-of
$(call register-ifneq,$(filter $(1),$(2)),,$(3))
endef

define register-if-none-of
$(call register-ifeq,$(filter $(1),$(2)),,$(3))
endef

define register-if-kconfig
$(call register-ifeq,$($(1)),y,$(2))
endef

define register-if-not-kconfig
$(call register-ifeq,$($(1)),,$(2))
endef
