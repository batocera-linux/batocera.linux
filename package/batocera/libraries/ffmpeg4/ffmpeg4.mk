################################################################################
#
# ffmpeg4
#
################################################################################

FFMPEG4_VERSION = 4.4.5
FFMPEG4_SOURCE = ffmpeg-$(FFMPEG4_VERSION).tar.xz
FFMPEG4_SITE = https://ffmpeg.org/releases
FFMPEG4_INSTALL_STAGING = YES

FFMPEG4_LICENSE = LGPL-2.1+, libjpeg license
FFMPEG4_LICENSE_FILES = LICENSE.md COPYING.LGPLv2.1
ifeq ($(BR2_PACKAGE_FFMPEG_GPL),y)
FFMPEG4_LICENSE += and GPL-2.0+
FFMPEG4_LICENSE_FILES += COPYING.GPLv2
endif

FFMPEG4_CPE_ID_VENDOR = ffmpeg

FFMPEG4_CONF_OPTS = \
	--prefix=/usr \
    --incdir=/usr/include/ffmpeg4.4 \
    --libdir=/usr/lib/ffmpeg4.4 \
	--enable-avfilter \
	--disable-version3 \
	--enable-logging \
	--enable-optimizations \
	--disable-extra-warnings \
	--enable-avdevice \
	--enable-avcodec \
	--enable-avformat \
	--enable-network \
	--disable-gray \
	--enable-swscale-alpha \
	--disable-small \
	--enable-dct \
	--enable-fft \
	--enable-mdct \
	--enable-rdft \
	--disable-crystalhd \
	--disable-dxva2 \
	--enable-runtime-cpudetect \
	--disable-hardcoded-tables \
	--disable-mipsdsp \
	--disable-mipsdspr2 \
	--disable-msa \
	--enable-hwaccels \
	--disable-cuda \
	--disable-cuvid \
	--disable-nvenc \
	--disable-avisynth \
	--disable-frei0r \
	--disable-libopencore-amrnb \
	--disable-libopencore-amrwb \
	--disable-libdc1394 \
	--disable-libgsm \
	--disable-libilbc \
	--disable-libvo-amrwbenc \
	--disable-symver \
	--disable-doc \
	--disable-programs # avoid overwriting ffmpeg 7

# batocera - add pulse audio support for batocera-record
ifeq ($(BR2_PACKAGE_PULSEAUDIO),y)
FFMPEG4_CONF_OPTS += --enable-libpulse
FFMPEG4_DEPENDENCIES += pulseaudio
endif

FFMPEG4_DEPENDENCIES += host-pkgconf

ifeq ($(BR2_PACKAGE_FFMPEG_GPL),y)
FFMPEG4_CONF_OPTS += --enable-gpl
else
FFMPEG4_CONF_OPTS += --disable-gpl
endif

ifeq ($(BR2_PACKAGE_FFMPEG_NONFREE),y)
FFMPEG4_CONF_OPTS += --enable-nonfree
else
FFMPEG4_CONF_OPTS += --disable-nonfree
endif

ifeq ($(BR2_PACKAGE_FFMPEG4_FFMPEG),y)
FFMPEG4_CONF_OPTS += --enable-ffmpeg
else
FFMPEG4_CONF_OPTS += --disable-ffmpeg
endif

ifeq ($(BR2_PACKAGE_FFMPEG_FFPLAY),y)
FFMPEG4_DEPENDENCIES += sdl2
FFMPEG4_CONF_OPTS += --enable-ffplay
FFMPEG4_CONF_ENV += SDL_CONFIG=$(STAGING_DIR)/usr/bin/sdl2-config
else
FFMPEG4_CONF_OPTS += --disable-ffplay
endif

ifeq ($(BR2_PACKAGE_LIBV4L),y)
FFMPEG4_DEPENDENCIES += libv4l
FFMPEG4_CONF_OPTS += --enable-libv4l2
else
FFMPEG4_CONF_OPTS += --disable-libv4l2
endif

ifeq ($(BR2_PACKAGE_FFMPEG_AVRESAMPLE),y)
FFMPEG4_CONF_OPTS += --enable-avresample
else
FFMPEG4_CONF_OPTS += --disable-avresample
endif

ifeq ($(BR2_PACKAGE_FFMPEG4_FFPROBE),y)
FFMPEG4_CONF_OPTS += --enable-ffprobe
else
FFMPEG4_CONF_OPTS += --disable-ffprobe
endif

ifeq ($(BR2_PACKAGE_FFMPEG_XCBGRAB),y)
FFMPEG4_CONF_OPTS += \
	--enable-libxcb \
	--enable-libxcb-shape \
	--enable-libxcb-shm \
	--enable-libxcb-xfixes
FFMPEG4_DEPENDENCIES += libxcb
else
FFMPEG4_CONF_OPTS += --disable-libxcb
endif

ifeq ($(BR2_PACKAGE_FFMPEG_POSTPROC),y)
FFMPEG4_CONF_OPTS += --enable-postproc
else
FFMPEG4_CONF_OPTS += --disable-postproc
endif

ifeq ($(BR2_PACKAGE_FFMPEG_SWSCALE),y)
FFMPEG4_CONF_OPTS += --enable-swscale
else
FFMPEG4_CONF_OPTS += --disable-swscale
endif

ifneq ($(call qstrip,$(BR2_PACKAGE_FFMPEG_ENCODERS)),all)
FFMPEG4_CONF_OPTS += --disable-encoders \
	$(foreach x,$(call qstrip,$(BR2_PACKAGE_FFMPEG_ENCODERS)),--enable-encoder=$(x))
endif

ifneq ($(call qstrip,$(BR2_PACKAGE_FFMPEG_DECODERS)),all)
FFMPEG4_CONF_OPTS += --disable-decoders \
	$(foreach x,$(call qstrip,$(BR2_PACKAGE_FFMPEG_DECODERS)),--enable-decoder=$(x))
endif

ifneq ($(call qstrip,$(BR2_PACKAGE_FFMPEG_MUXERS)),all)
FFMPEG4_CONF_OPTS += --disable-muxers \
	$(foreach x,$(call qstrip,$(BR2_PACKAGE_FFMPEG_MUXERS)),--enable-muxer=$(x))
endif

ifneq ($(call qstrip,$(BR2_PACKAGE_FFMPEG_DEMUXERS)),all)
FFMPEG4_CONF_OPTS += --disable-demuxers \
	$(foreach x,$(call qstrip,$(BR2_PACKAGE_FFMPEG_DEMUXERS)),--enable-demuxer=$(x))
endif

ifneq ($(call qstrip,$(BR2_PACKAGE_FFMPEG_PARSERS)),all)
FFMPEG4_CONF_OPTS += --disable-parsers \
	$(foreach x,$(call qstrip,$(BR2_PACKAGE_FFMPEG_PARSERS)),--enable-parser=$(x))
endif

ifneq ($(call qstrip,$(BR2_PACKAGE_FFMPEG_BSFS)),all)
FFMPEG4_CONF_OPTS += --disable-bsfs \
	$(foreach x,$(call qstrip,$(BR2_PACKAGE_FFMPEG_BSFS)),--enable-bsf=$(x))
endif

ifneq ($(call qstrip,$(BR2_PACKAGE_FFMPEG_PROTOCOLS)),all)
FFMPEG4_CONF_OPTS += --disable-protocols \
	$(foreach x,$(call qstrip,$(BR2_PACKAGE_FFMPEG_PROTOCOLS)),--enable-protocol=$(x))
endif

ifneq ($(call qstrip,$(BR2_PACKAGE_FFMPEG_FILTERS)),all)
FFMPEG4_CONF_OPTS += --disable-filters \
	$(foreach x,$(call qstrip,$(BR2_PACKAGE_FFMPEG_FILTERS)),--enable-filter=$(x))
endif

ifeq ($(BR2_PACKAGE_FFMPEG_INDEVS),y)
FFMPEG4_CONF_OPTS += --enable-indevs
ifeq ($(BR2_PACKAGE_ALSA_LIB),y)
FFMPEG4_CONF_OPTS += --enable-alsa
FFMPEG4_DEPENDENCIES += alsa-lib
else
FFMPEG4_CONF_OPTS += --disable-alsa
endif
else
FFMPEG4_CONF_OPTS += --disable-indevs
endif

ifeq ($(BR2_PACKAGE_FFMPEG_OUTDEVS),y)
FFMPEG4_CONF_OPTS += --enable-outdevs
ifeq ($(BR2_PACKAGE_ALSA_LIB),y)
FFMPEG4_DEPENDENCIES += alsa-lib
endif
else
FFMPEG4_CONF_OPTS += --disable-outdevs
endif

ifeq ($(BR2_TOOLCHAIN_HAS_THREADS),y)
FFMPEG4_CONF_OPTS += --enable-pthreads
else
FFMPEG4_CONF_OPTS += --disable-pthreads
endif

ifeq ($(BR2_PACKAGE_ZLIB),y)
FFMPEG4_CONF_OPTS += --enable-zlib
FFMPEG4_DEPENDENCIES += zlib
else
FFMPEG4_CONF_OPTS += --disable-zlib
endif

ifeq ($(BR2_PACKAGE_BZIP2),y)
FFMPEG4_CONF_OPTS += --enable-bzlib
FFMPEG4_DEPENDENCIES += bzip2
else
FFMPEG4_CONF_OPTS += --disable-bzlib
endif

ifeq ($(BR2_PACKAGE_FDK_AAC)$(BR2_PACKAGE_FFMPEG_NONFREE),yy)
FFMPEG4_CONF_OPTS += --enable-libfdk-aac
FFMPEG4_DEPENDENCIES += fdk-aac
else
FFMPEG4_CONF_OPTS += --disable-libfdk-aac
endif

ifeq ($(BR2_PACKAGE_FFMPEG_GPL)$(BR2_PACKAGE_LIBCDIO_PARANOIA),yy)
FFMPEG4_CONF_OPTS += --enable-libcdio
FFMPEG4_DEPENDENCIES += libcdio-paranoia
else
FFMPEG4_CONF_OPTS += --disable-libcdio
endif

ifeq ($(BR2_PACKAGE_GNUTLS),y)
FFMPEG4_CONF_OPTS += --enable-gnutls --disable-openssl
FFMPEG4_DEPENDENCIES += gnutls
else
FFMPEG4_CONF_OPTS += --disable-gnutls
ifeq ($(BR2_PACKAGE_OPENSSL),y)
# openssl isn't license compatible with GPL
ifeq ($(BR2_PACKAGE_FFMPEG_GPL)x$(BR2_PACKAGE_FFMPEG_NONFREE),yx)
FFMPEG4_CONF_OPTS += --disable-openssl
else
FFMPEG4_CONF_OPTS += --enable-openssl
FFMPEG4_DEPENDENCIES += openssl
endif
else
FFMPEG4_CONF_OPTS += --disable-openssl
endif
endif

ifeq ($(BR2_PACKAGE_FFMPEG_GPL)$(BR2_PACKAGE_LIBEBUR128),yy)
FFMPEG4_DEPENDENCIES += libebur128
endif

ifeq ($(BR2_PACKAGE_LIBDRM),y)
FFMPEG4_CONF_OPTS += --enable-libdrm
FFMPEG4_DEPENDENCIES += libdrm
else
FFMPEG4_CONF_OPTS += --disable-libdrm
endif

ifeq ($(BR2_PACKAGE_LIBOPENH264),y)
FFMPEG4_CONF_OPTS += --enable-libopenh264
FFMPEG4_DEPENDENCIES += libopenh264
else
FFMPEG4_CONF_OPTS += --disable-libopenh264
endif

ifeq ($(BR2_PACKAGE_LIBVORBIS),y)
FFMPEG4_DEPENDENCIES += libvorbis
FFMPEG4_CONF_OPTS += \
	--enable-libvorbis \
	--enable-muxer=ogg \
	--enable-encoder=libvorbis
endif

ifeq ($(BR2_PACKAGE_LIBVA),y)
FFMPEG4_CONF_OPTS += --enable-vaapi
FFMPEG4_DEPENDENCIES += libva
else
FFMPEG4_CONF_OPTS += --disable-vaapi
endif

ifeq ($(BR2_PACKAGE_LIBVDPAU),y)
FFMPEG4_CONF_OPTS += --enable-vdpau
FFMPEG4_DEPENDENCIES += libvdpau
else
FFMPEG4_CONF_OPTS += --disable-vdpau
endif

ifeq ($(BR2_PACKAGE_RPI_USERLAND),y)
FFMPEG4_CONF_OPTS += --enable-omx --enable-omx-rpi \
	--extra-cflags=-I$(STAGING_DIR)/usr/include/IL
FFMPEG4_DEPENDENCIES += rpi-userland
ifeq ($(BR2_arm),y)
FFMPEG4_CONF_OPTS += --enable-mmal
else
FFMPEG4_CONF_OPTS += --disable-mmal
endif
else
FFMPEG4_CONF_OPTS += --disable-mmal --disable-omx --disable-omx-rpi
endif

# Required for hw decoding on raspberry pi boards
ifeq ($(BR2_PACKAGE_RPI_HEVC),y)
FFMPEG4_CONF_OPTS += --disable-mmal
FFMPEG4_CONF_OPTS += --enable-neon
FFMPEG4_CONF_OPTS += --enable-v4l2-request
FFMPEG4_CONF_OPTS += --enable-libudev
FFMPEG4_CONF_OPTS += --enable-epoxy
FFMPEG4_CONF_OPTS += --enable-sand
endif

# To avoid a circular dependency only use opencv if opencv itself does
# not depend on ffmpeg.
ifeq ($(BR2_PACKAGE_OPENCV3_LIB_IMGPROC)x$(BR2_PACKAGE_OPENCV3_WITH_FFMPEG),yx)
FFMPEG4_CONF_OPTS += --enable-libopencv
FFMPEG4_DEPENDENCIES += opencv3
else
FFMPEG4_CONF_OPTS += --disable-libopencv
endif

ifeq ($(BR2_PACKAGE_OPUS),y)
FFMPEG4_CONF_OPTS += --enable-libopus
FFMPEG4_DEPENDENCIES += opus
else
FFMPEG4_CONF_OPTS += --disable-libopus
endif

ifeq ($(BR2_PACKAGE_LIBVPX),y)
FFMPEG4_CONF_OPTS += --enable-libvpx
FFMPEG4_DEPENDENCIES += libvpx
else
FFMPEG4_CONF_OPTS += --disable-libvpx
endif

ifeq ($(BR2_PACKAGE_LIBASS),y)
FFMPEG4_CONF_OPTS += --enable-libass
FFMPEG4_DEPENDENCIES += libass
else
FFMPEG4_CONF_OPTS += --disable-libass
endif

ifeq ($(BR2_PACKAGE_LIBBLURAY),y)
FFMPEG4_CONF_OPTS += --enable-libbluray
FFMPEG4_DEPENDENCIES += libbluray
else
FFMPEG4_CONF_OPTS += --disable-libbluray
endif

ifeq ($(BR2_PACKAGE_INTEL_MEDIASDK),y)
FFMPEG4_CONF_OPTS += --enable-libmfx
FFMPEG4_DEPENDENCIES += intel-mediasdk
else
FFMPEG4_CONF_OPTS += --disable-libmfx
endif

ifeq ($(BR2_PACKAGE_RTMPDUMP),y)
FFMPEG4_CONF_OPTS += --enable-librtmp
FFMPEG4_DEPENDENCIES += rtmpdump
else
FFMPEG4_CONF_OPTS += --disable-librtmp
endif

ifeq ($(BR2_PACKAGE_LAME),y)
FFMPEG4_CONF_OPTS += --enable-libmp3lame
FFMPEG4_DEPENDENCIES += lame
else
FFMPEG4_CONF_OPTS += --disable-libmp3lame
endif

ifeq ($(BR2_PACKAGE_LIBMODPLUG),y)
FFMPEG4_CONF_OPTS += --enable-libmodplug
FFMPEG4_DEPENDENCIES += libmodplug
else
FFMPEG4_CONF_OPTS += --disable-libmodplug
endif

ifeq ($(BR2_PACKAGE_SPEEX),y)
FFMPEG4_CONF_OPTS += --enable-libspeex
FFMPEG4_DEPENDENCIES += speex
else
FFMPEG4_CONF_OPTS += --disable-libspeex
endif

ifeq ($(BR2_PACKAGE_LIBTHEORA),y)
FFMPEG4_CONF_OPTS += --enable-libtheora
FFMPEG4_DEPENDENCIES += libtheora
else
FFMPEG4_CONF_OPTS += --disable-libtheora
endif

ifeq ($(BR2_PACKAGE_LIBICONV),y)
FFMPEG4_CONF_OPTS += --enable-iconv
FFMPEG4_DEPENDENCIES += libiconv
else
FFMPEG4_CONF_OPTS += --disable-iconv
endif

# batocera - add cuda
ifeq ($(BR2_PACKAGE_NVIDIA_OPEN_DRIVER_CUDA),y)
FFMPEG4_CONF_OPTS += --enable-cuda
FFMPEG4_DEPENDENCIES += nv-codec-headers
endif

# ffmpeg freetype support require fenv.h which is only
# available/working on glibc.
# The microblaze variant doesn't provide the needed exceptions
ifeq ($(BR2_PACKAGE_FREETYPE)$(BR2_TOOLCHAIN_USES_GLIBC)x$(BR2_microblaze),yyx)
FFMPEG4_CONF_OPTS += --enable-libfreetype
FFMPEG4_DEPENDENCIES += freetype
else
FFMPEG4_CONF_OPTS += --disable-libfreetype
endif

ifeq ($(BR2_PACKAGE_FONTCONFIG),y)
FFMPEG4_CONF_OPTS += --enable-fontconfig
FFMPEG4_DEPENDENCIES += fontconfig
else
FFMPEG4_CONF_OPTS += --disable-fontconfig
endif

ifeq ($(BR2_PACKAGE_OPENJPEG),y)
FFMPEG4_CONF_OPTS += --enable-libopenjpeg
FFMPEG4_DEPENDENCIES += openjpeg
else
FFMPEG4_CONF_OPTS += --disable-libopenjpeg
endif

ifeq ($(BR2_PACKAGE_X264)$(BR2_PACKAGE_FFMPEG_GPL),yy)
FFMPEG4_CONF_OPTS += --enable-libx264
FFMPEG4_DEPENDENCIES += x264
else
FFMPEG4_CONF_OPTS += --disable-libx264
endif

ifeq ($(BR2_PACKAGE_X265)$(BR2_PACKAGE_FFMPEG_GPL),yy)
FFMPEG4_CONF_OPTS += --enable-libx265
FFMPEG4_DEPENDENCIES += x265
else
FFMPEG4_CONF_OPTS += --disable-libx265
endif

ifeq ($(BR2_PACKAGE_DAV1D),y)
FFMPEG4_CONF_OPTS += --enable-libdav1d
FFMPEG4_DEPENDENCIES += dav1d
else
FFMPEG4_CONF_OPTS += --disable-libdav1d
endif

ifeq ($(BR2_X86_CPU_HAS_MMX),y)
FFMPEG4_CONF_OPTS += --enable-x86asm
FFMPEG4_DEPENDENCIES += host-nasm
else
FFMPEG4_CONF_OPTS += --disable-x86asm
FFMPEG4_CONF_OPTS += --disable-mmx
endif

ifeq ($(BR2_X86_CPU_HAS_SSE),y)
FFMPEG4_CONF_OPTS += --enable-sse
else
FFMPEG4_CONF_OPTS += --disable-sse
endif

ifeq ($(BR2_X86_CPU_HAS_SSE2),y)
FFMPEG4_CONF_OPTS += --enable-sse2
else
FFMPEG4_CONF_OPTS += --disable-sse2
endif

ifeq ($(BR2_X86_CPU_HAS_SSE3),y)
FFMPEG4_CONF_OPTS += --enable-sse3
else
FFMPEG4_CONF_OPTS += --disable-sse3
endif

ifeq ($(BR2_X86_CPU_HAS_SSSE3),y)
FFMPEG4_CONF_OPTS += --enable-ssse3
else
FFMPEG4_CONF_OPTS += --disable-ssse3
endif

ifeq ($(BR2_X86_CPU_HAS_SSE4),y)
FFMPEG4_CONF_OPTS += --enable-sse4
else
FFMPEG4_CONF_OPTS += --disable-sse4
endif

ifeq ($(BR2_X86_CPU_HAS_SSE42),y)
FFMPEG4_CONF_OPTS += --enable-sse42
else
FFMPEG4_CONF_OPTS += --disable-sse42
endif

ifeq ($(BR2_X86_CPU_HAS_AVX),y)
FFMPEG4_CONF_OPTS += --enable-avx
else
FFMPEG4_CONF_OPTS += --disable-avx
endif

ifeq ($(BR2_X86_CPU_HAS_AVX2),y)
FFMPEG4_CONF_OPTS += --enable-avx2
else
FFMPEG4_CONF_OPTS += --disable-avx2
endif

# Explicitly disable everything that doesn't match for ARM
# FFMPEG "autodetects" by compiling an extended instruction via AS
# This works on compilers that aren't built for generic by default
ifeq ($(BR2_ARM_CPU_ARMV4),y)
FFMPEG4_CONF_OPTS += --disable-armv5te
endif
ifeq ($(BR2_ARM_CPU_ARMV6)$(BR2_ARM_CPU_ARMV7A),y)
FFMPEG4_CONF_OPTS += --enable-armv6
else
FFMPEG4_CONF_OPTS += --disable-armv6 --disable-armv6t2
endif
ifeq ($(BR2_ARM_CPU_HAS_VFPV2),y)
FFMPEG4_CONF_OPTS += --enable-vfp
else
FFMPEG4_CONF_OPTS += --disable-vfp
endif
ifeq ($(BR2_ARM_CPU_HAS_NEON),y)
FFMPEG4_CONF_OPTS += --enable-neon
else ifeq ($(BR2_aarch64),y)
FFMPEG4_CONF_OPTS += --enable-neon
else
FFMPEG4_CONF_OPTS += --disable-neon
endif

ifeq ($(BR2_mips)$(BR2_mipsel)$(BR2_mips64)$(BR2_mips64el),y)
ifeq ($(BR2_MIPS_SOFT_FLOAT),y)
FFMPEG4_CONF_OPTS += --disable-mipsfpu
else
FFMPEG4_CONF_OPTS += --enable-mipsfpu
endif

# Fix build failure on several missing assembly instructions
FFMPEG4_CONF_OPTS += --disable-asm
endif # MIPS

ifeq ($(BR2_POWERPC_CPU_HAS_ALTIVEC):$(BR2_powerpc64le),y:)
FFMPEG4_CONF_OPTS += --enable-altivec
else ifeq ($(BR2_POWERPC_CPU_HAS_VSX):$(BR2_powerpc64le),y:y)
# On LE, ffmpeg AltiVec support needs VSX intrinsics, and VSX
# is an extension to AltiVec.
FFMPEG4_CONF_OPTS += --enable-altivec
else
FFMPEG4_CONF_OPTS += --disable-altivec
endif

# Uses __atomic_fetch_add_4
ifeq ($(BR2_TOOLCHAIN_HAS_LIBATOMIC),y)
FFMPEG4_CONF_OPTS += --extra-libs=-latomic
endif

ifeq ($(BR2_STATIC_LIBS),)
FFMPEG4_CONF_OPTS += --enable-pic
else
FFMPEG4_CONF_OPTS += --disable-pic
endif

# Default to --cpu=generic for MIPS architecture, in order to avoid a
# warning from ffmpeg's configure script.
ifeq ($(BR2_mips)$(BR2_mipsel)$(BR2_mips64)$(BR2_mips64el),y)
FFMPEG4_CONF_OPTS += --cpu=generic
else ifneq ($(GCC_TARGET_CPU),)
FFMPEG4_CONF_OPTS += --cpu="$(GCC_TARGET_CPU)"
else ifneq ($(GCC_TARGET_ARCH),)
FFMPEG4_CONF_OPTS += --cpu="$(GCC_TARGET_ARCH)"
endif

FFMPEG4_CFLAGS = $(TARGET_CFLAGS)

ifeq ($(BR2_TOOLCHAIN_HAS_GCC_BUG_85180),y)
FFMPEG4_CONF_OPTS += --disable-optimizations
FFMPEG4_CFLAGS += -O0
endif

ifeq ($(BR2_ARM_INSTRUCTIONS_THUMB),y)
FFMPEG4_CFLAGS += -marm
endif

FFMPEG4_CONF_ENV += CFLAGS="$(FFMPEG4_CFLAGS)"
FFMPEG4_CONF_OPTS += $(call qstrip,$(BR2_PACKAGE_FFMPEG_EXTRACONF))

# Override FFMPEG4_CONFIGURE_CMDS: FFmpeg does not support --target and others
define FFMPEG4_CONFIGURE_CMDS
	(cd $(FFMPEG4_SRCDIR) && rm -rf config.cache && \
	$(TARGET_CONFIGURE_OPTS) \
	$(TARGET_CONFIGURE_ARGS) \
	$(FFMPEG4_CONF_ENV) \
	./configure \
		--enable-cross-compile \
		--cross-prefix=$(TARGET_CROSS) \
		--sysroot=$(STAGING_DIR) \
		--host-cc="$(HOSTCC)" \
		--arch=$(BR2_ARCH) \
		--target-os="linux" \
		--disable-stripping \
		--pkg-config="$(PKG_CONFIG_HOST_BINARY)" \
		$(SHARED_STATIC_LIBS_OPTS) \
		$(FFMPEG4_CONF_OPTS) \
	)
endef

define FFMPEG4_REMOVE_EXAMPLE_SRC_FILES
	rm -rf $(TARGET_DIR)/usr/share/ffmpeg/examples
	# move libraries & fix symbolic links
	cd $(TARGET_DIR)/usr/lib/ffmpeg4.4 && \
	for f in *; do \
		if [[ $$f == *.so ]]; then \
			ln -srf -- $(TARGET_DIR)/usr/lib/"$$(readlink "$$f")" "$$f"; \
		elif [[ ! -d $$f ]]; then \
			mv "$$f" $(TARGET_DIR)/usr/lib; \
		fi \
	done
endef

FFMPEG4_POST_INSTALL_TARGET_HOOKS += FFMPEG4_REMOVE_EXAMPLE_SRC_FILES

$(eval $(autotools-package))
