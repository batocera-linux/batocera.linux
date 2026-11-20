################################################################################
#
# dsp56300
#
################################################################################

DSP56300_VERSION = v0.1.3
DSP56300_SITE = $(call github,mborgerson,dsp56300,$(DSP56300_VERSION))
DSP56300_LICENSE = MIT
DSP56300_LICENSE_FILES = LICENSE
DSP56300_INSTALL_STAGING = YES
DSP56300_INSTALL_TARGET = NO

DSP56300_CARGO_BUILD_OPTS = -p dsp56300-emu-ffi

define DSP56300_INSTALL_STAGING_CMDS
	$(INSTALL) -D -m 0644 \
	    $(@D)/target/$(RUSTC_TARGET_NAME)/release/libdsp56300_emu_ffi.a \
	    $(STAGING_DIR)/usr/lib/libdsp56300_emu_ffi.a
	$(INSTALL) -D -m 0644 $(@D)/crates/emu-ffi/include/dsp56300.h \
	    $(STAGING_DIR)/usr/include/dsp56300.h
	mkdir -p $(STAGING_DIR)/usr/lib/pkgconfig
	printf '%s\n' \
	    'prefix=/usr' \
	    'libdir=$${prefix}/lib' \
	    'includedir=$${prefix}/include' \
	    '' \
	    'Name: dsp56300-emu-ffi' \
	    'Description: DSP56300 JIT emulator C API' \
	    'Version: $(patsubst v%,%,$(DSP56300_VERSION))' \
	    'Libs: -L$${libdir} -ldsp56300_emu_ffi -lpthread -ldl -lm' \
	    'Cflags: -I$${includedir}' \
	    > $(STAGING_DIR)/usr/lib/pkgconfig/dsp56300-emu-ffi.pc
endef

$(eval $(cargo-package))
