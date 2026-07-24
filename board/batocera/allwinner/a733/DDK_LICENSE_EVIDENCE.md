# PowerVR DDK License Evidence

This file records the provenance and licensing basis for the PowerVR BXM-4-64 DDK
userspace libraries bundled in `fsoverlay/usr/local/lib/` and `fsoverlay/usr/lib/`.

## Package Details

| Field | Value |
|-------|-------|
| Package | `xserver-xorg-img-bxm` |
| Version | `1.21.1-2` |
| Architecture | `arm64` |
| DDK Version | `24.2.6603887` |
| BVNC | `36.56.104.183` |
| **Section** | **`free`** |
| **Maintainer** | **`Allwinnertech`** |
| Source repo | Radxa a733-bullseye apt repository |

## What "Section: free" Means

In Debian packaging, `Section: free` means the package is compliant with the
[Debian Free Software Guidelines (DFSG)](https://www.debian.org/social_contract#guidelines) —
software that can be freely used, modified, and redistributed. This classification
is set by the package maintainer (Allwinnertech, the SoC vendor) in the package
control file.

**This is the SoC vendor itself declaring their DDK to be freely distributable.**

## Contrast: Other PVR DDK Packages

The Batocera upstream `img-gpu-powervr` package for StarFive/JH7110 explicitly states:
```
IMG_GPU_POWERVR_LICENSE = Strictly Confidential
IMG_GPU_POWERVR_REDISTRIBUTE = NO
```

Our package has the opposite declaration.

## Secondary Evidence: Public GitHub Distribution

The same DDK binaries (DDK 24.2, BVNC 36.56.104.183, arm64) are also distributed
openly on GitHub by the Deepin Linux project:

- Repository: `https://github.com/deepin-community/img-gpu-bin`
- Path: `bin/ddk242/36.56.104.183/arm64/`
- Files distributed publicly without any access restrictions

This represents a second independent party (Deepin/UOS, a major Chinese Linux
distribution) distributing the same binaries publicly, consistent with Allwinnertech's
"free" classification.

## Files Included

From `xserver-xorg-img-bxm_1.21.1-2_arm64.deb`:

**`/usr/local/lib/`**
- `libEGL.so.1.0.0`
- `libGLESv2.so.2.0.0`
- `libGLESv1_CM.so.1.1.0`
- `libgbm.so.1.0.0`
- `libglapi.so.0.0.0`
- `libvulkan.so.1.3.280`
- `libpvr_mesa_wsi.so`
- `dri/pvr_dri.so`
- `dri/sunxi-drm_dri.so`
- `dri/swrast_dri.so`

**`/usr/lib/`**
- `libGLESv2_PVR_MESA.so.24.2.6603887`
- `libGLESv1_CM_PVR_MESA.so.24.2.6603887`
- `libsrv_um.so.24.2.6603887`
- `libglslcompiler.so.24.2.6603887`
- `libpvr_dri_support.so.24.2.6603887`
- `libPVROCL.so.24.2.6603887`
- `libPVRScopeServices.so.24.2.6603887`
- `libsutu_display.so.24.2.6603887`
- `libufwriter.so.24.2.6603887`
- `libusc.so.24.2.6603887`
- `libVK_IMG.so.24.2.6603887`
