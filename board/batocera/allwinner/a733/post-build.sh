#!/bin/bash
# Allwinner A733 / Radxa Cubie A7S post-build script
# Called by Buildroot after the rootfs is assembled, before squashfs packing.
# $1 = TARGET_DIR
set -euo pipefail

TARGET_DIR="$1"

CROSS="${HOST_DIR}/bin/aarch64-buildroot-linux-gnu-"

# =============================================================================
# Build pvrsrvkm.ko (Imagination PowerVR BXM-4-64 kernel module)
#
# The module source lives in bsp/modules/gpu/ inside the kernel tree, which is
# pre-merged into https://github.com/GameOctane/allwinner-a733-linux.
# Buildroot downloads the kernel to BUILD_DIR/linux-custom; the GPU module
# source is therefore at BUILD_DIR/linux-custom/bsp/modules/gpu/.
#
# The module cannot be built in-tree via Kbuild obj-m because the GPU Makefile
# uses the Allwinner sunxi_linux build system. We invoke its 'build' target
# directly out-of-tree here, after the kernel has been compiled.
# =============================================================================
KERNEL_BUILD="${BUILD_DIR}/linux-custom"
GPU_MODULE_DIR="${KERNEL_BUILD}/bsp/modules/gpu"

if [ ! -d "${GPU_MODULE_DIR}" ]; then
    echo "[post-build] WARNING: GPU module source not found at ${GPU_MODULE_DIR}"
    echo "[post-build] Expected bsp/modules/gpu/ inside the kernel source tree."
    exit 0
fi

echo "[post-build] Building pvrsrvkm.ko (PowerVR BXM-4-64)..."
echo "[post-build]   Kernel build : ${KERNEL_BUILD}"
echo "[post-build]   GPU source   : ${GPU_MODULE_DIR}"

# The GPU Makefile uses a custom build system, not Kbuild obj-m.
# Export CROSS_COMPILE and KERNELDIR as env vars — the inner -Rr make
# invocation suppresses variable propagation, so env vars are the only
# reliable way to pass them through. sunxi_linux/Makefile uses
# LICHEE_TOOLCHAIN_PATH/LICHEE_CROSS_COMPILER to resolve the toolchain prefix.
export CROSS_COMPILE="${CROSS}"
export KERNELDIR="${KERNEL_BUILD}"
export ARCH=arm64
export LICHEE_TOOLCHAIN_PATH="${HOST_DIR}"
export LICHEE_CROSS_COMPILER="aarch64-buildroot-linux-gnu"
make -C "${GPU_MODULE_DIR}" build \
    KERNEL_SRC_DIR="${KERNEL_BUILD}" \
    KERNEL_OUT_DIR="${KERNEL_BUILD}" \
    KERNELDIR="${KERNEL_BUILD}" \
    KDIR="${KERNEL_BUILD}" \
    ARCH=arm64 \
    CROSS_COMPILE="${CROSS}" \
    LICHEE_TOOLCHAIN_PATH="${HOST_DIR}" \
    LICHEE_CROSS_COMPILER="aarch64-buildroot-linux-gnu" \
    CPU_ARCH=arm64 \
    GPU_TYPE=bxm \
    CONFIG_OS_TYPE=linux \
    GPU_BUILD_TYPE=release \
    -j$(nproc)

# Find built .ko files and install them
KVER=$(cat "${KERNEL_BUILD}/include/config/kernel.release" 2>/dev/null || \
       awk -F\" '/UTS_RELEASE/{print $2}' "${KERNEL_BUILD}/include/generated/utsrelease.h" 2>/dev/null || \
       echo "unknown")

KO_DEST="${TARGET_DIR}/lib/modules/${KVER}/extra"
mkdir -p "${KO_DEST}"

# Output lands in binary_sunxi_linux_nulldrmws_release/target_aarch64/kbuild/
KO_SRC=$(find "${GPU_MODULE_DIR}/img-bxm" -name "pvrsrvkm.ko" 2>/dev/null | head -1)
if [ -z "${KO_SRC}" ]; then
    echo "[post-build] ERROR: pvrsrvkm.ko not found after build"
    exit 1
fi
"${CROSS}strip" --strip-debug "${KO_SRC}" -o "${KO_DEST}/pvrsrvkm.ko"
echo "[post-build] Installed: ${KO_DEST}/pvrsrvkm.ko  (from ${KO_SRC})"

echo "[post-build] pvrsrvkm.ko done."
