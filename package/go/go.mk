################################################################################
#
# go
#
################################################################################

GO_VERSION = 1.12.9
GO_SITE = https://storage.googleapis.com/golang
GO_SOURCE = go$(GO_VERSION).src.tar.gz

GO_LICENSE = BSD-3-Clause
GO_LICENSE_FILES = LICENSE

HOST_GO_DEPENDENCIES = host-go-bootstrap
HOST_GO_HOST_CACHE = $(HOST_DIR)/usr/share/host-go-cache
HOST_GO_ROOT = $(HOST_DIR)/lib/go
HOST_GO_TARGET_CACHE = $(HOST_DIR)/usr/share/go-cache

ifeq ($(BR2_PACKAGE_HOST_GO_TARGET_ARCH_SUPPORTS),y)

ifeq ($(BR2_arm),y)
GO_GOARCH = arm
ifeq ($(BR2_ARM_CPU_ARMV5),y)
GO_GOARM = 5
else ifeq ($(BR2_ARM_CPU_ARMV6),y)
GO_GOARM = 6
else ifeq ($(BR2_ARM_CPU_ARMV7A),y)
GO_GOARM = 7
endif
else ifeq ($(BR2_aarch64),y)
GO_GOARCH = arm64
else ifeq ($(BR2_i386),y)
GO_GOARCH = 386
else ifeq ($(BR2_x86_64),y)
GO_GOARCH = amd64
else ifeq ($(BR2_powerpc64),y)
GO_GOARCH = ppc64
else ifeq ($(BR2_powerpc64le),y)
GO_GOARCH = ppc64le
else ifeq ($(BR2_mips64),y)
GO_GOARCH = mips64
else ifeq ($(BR2_mips64el),y)
GO_GOARCH = mips64le
endif

# For the convienience of target packages.
HOST_GO_TOOLDIR = $(HOST_GO_ROOT)/pkg/tool/linux_$(GO_GOARCH)
HOST_GO_TARGET_ENV = \
	GO111MODULE=off \
	GOARCH=$(GO_GOARCH) \
	GOCACHE="$(HOST_GO_TARGET_CACHE)" \
	GOROOT="$(HOST_GO_ROOT)" \
	CC="$(TARGET_CC)" \
	CXX="$(TARGET_CXX)" \
	GOTOOLDIR="$(HOST_GO_TOOLDIR)"

# The go compiler's cgo support uses threads.  If BR2_TOOLCHAIN_HAS_THREADS is
# set, build in cgo support for any go programs that may need it.  Note that
# any target package needing cgo support must include
# 'depends on BR2_TOOLCHAIN_HAS_THREADS' in its config file.
ifeq ($(BR2_TOOLCHAIN_HAS_THREADS),y)
HOST_GO_CGO_ENABLED = 1
else
HOST_GO_CGO_ENABLED = 0
endif

HOST_GO_CROSS_ENV = \
	CC_FOR_TARGET="$(TARGET_CC)" \
	CXX_FOR_TARGET="$(TARGET_CXX)" \
	GOARCH=$(GO_GOARCH) \
	$(if $(GO_GOARM),GOARM=$(GO_GOARM)) \
	GO_ASSUME_CROSSCOMPILING=1

else # !BR2_PACKAGE_HOST_GO_TARGET_ARCH_SUPPORTS
# host-go can still be used to build packages for the host. No need to set all
# the arch stuff since we will not be cross-compiling.
HOST_GO_CGO_ENABLED = 1
endif # BR2_PACKAGE_HOST_GO_TARGET_ARCH_SUPPORTS

# The go build system is not compatible with ccache, so use
# HOSTCC_NOCCACHE.  See https://github.com/golang/go/issues/11685.
HOST_GO_MAKE_ENV = \
	GO111MODULE=off \
	GOCACHE=$(HOST_GO_HOST_CACHE) \
	GOROOT_BOOTSTRAP=$(HOST_GO_BOOTSTRAP_ROOT) \
	GOROOT_FINAL=$(HOST_GO_ROOT) \
	GOROOT="$(@D)" \
	GOBIN="$(@D)/bin" \
	GOOS=linux \
	CC=$(HOSTCC_NOCCACHE) \
	CXX=$(HOSTCXX_NOCCACHE) \
	CGO_ENABLED=$(HOST_GO_CGO_ENABLED) \
	$(HOST_GO_CROSS_ENV)

define HOST_GO_BUILD_CMDS
	cd $(@D)/src && \
		$(HOST_GO_MAKE_ENV) ./make.bash $(if $(VERBOSE),-v)
endef

define HOST_GO_INSTALL_CMDS
	$(INSTALL) -D -m 0755 $(@D)/bin/go $(HOST_GO_ROOT)/bin/go
	$(INSTALL) -D -m 0755 $(@D)/bin/gofmt $(HOST_GO_ROOT)/bin/gofmt

	ln -sf ../lib/go/bin/go $(HOST_DIR)/bin/
	ln -sf ../lib/go/bin/gofmt $(HOST_DIR)/bin/

	cp -a $(@D)/lib $(HOST_GO_ROOT)/

	mkdir -p $(HOST_GO_ROOT)/pkg
	cp -a $(@D)/pkg/include $(@D)/pkg/linux_* $(HOST_GO_ROOT)/pkg/
	cp -a $(@D)/pkg/tool $(HOST_GO_ROOT)/pkg/

	# There is a known issue which requires the go sources to be installed
	# https://golang.org/issue/2775
	cp -a $(@D)/src $(HOST_GO_ROOT)/

	# Set all file timestamps to prevent the go compiler from rebuilding any
	# built in packages when programs are built.
	find $(HOST_GO_ROOT) -type f -exec touch -r $(@D)/bin/go {} \;
endef

$(eval $(host-generic-package))
