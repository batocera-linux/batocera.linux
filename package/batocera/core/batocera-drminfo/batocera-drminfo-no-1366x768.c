/*
 * modeset - DRM Modesetting Example -- modified for batocera
 *
 * Written 2012-2013 by David Herrmann <dh.herrmann@googlemail.com>
 * Dedicated to the Public Domain.
 */

/*
 * Modesetting Example
 * This example is based on:
 *   https://github.com/dvdhrm/docs/blob/master/drm-howto/modeset.c
 *
 * What does it do?
 *   It opens a single DRM-card device node, assigns a CRTC+encoder to each
 *   connector that is connected and creates a framebuffer (DRM-dumb buffers)
 *   for each CRTC that is in use.
 *   It then draws a changing color value for 5s on all framebuffers and exits.
 */

#define _GNU_SOURCE
#include <errno.h>
#include <fcntl.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
#include <time.h>
#include <unistd.h>
#include <xf86drm.h>
#include <xf86drmMode.h>

struct modeset_dev {
	struct modeset_dev *next;

	uint32_t width;
	uint32_t height;
	uint32_t stride;
	uint32_t size;
	uint32_t handle;
	uint8_t *map;

	drmModeModeInfo mode;
	uint32_t fb;
	uint32_t conn;
	uint32_t crtc;
};

static struct modeset_dev *modeset_list = NULL;

static int modeset_find_crtc(int fd, drmModeRes *res, drmModeConnector *conn,
			     struct modeset_dev *dev)
{
	drmModeEncoder *enc;
	unsigned int i, j;
	int32_t crtc;
	struct modeset_dev *iter;

	/* first try the currently conected encoder+crtc */
	if (conn->encoder_id)
		enc = drmModeGetEncoder(fd, conn->encoder_id);
	else
		enc = NULL;

	if (enc) {
		if (enc->crtc_id) {
			crtc = enc->crtc_id;
			for (iter = modeset_list; iter; iter = iter->next) {
				if (iter->crtc == crtc) {
					crtc = -1;
					break;
				}
			}

			if (crtc >= 0) {
				drmModeFreeEncoder(enc);
				dev->crtc = crtc;
				return 0;
			}
		}

		drmModeFreeEncoder(enc);
	}

	/* If the connector is not currently bound to an encoder or if the
	 * encoder+crtc is already used by another connector (actually unlikely
	 * but lets be safe), iterate all other available encoders to find a
	 * matching CRTC. */
	for (i = 0; i < conn->count_encoders; ++i) {
		enc = drmModeGetEncoder(fd, conn->encoders[i]);
		if (!enc) {
			fprintf(stderr, "cannot retrieve encoder %u:%u (%d): %m\n",
				i, conn->encoders[i], errno);
			continue;
		}

		/* iterate all global CRTCs */
		for (j = 0; j < res->count_crtcs; ++j) {
			/* check whether this CRTC works with the encoder */
			if (!(enc->possible_crtcs & (1 << j)))
				continue;

			/* check that no other device already uses this CRTC */
			crtc = res->crtcs[j];
			for (iter = modeset_list; iter; iter = iter->next) {
				if (iter->crtc == crtc) {
					crtc = -1;
					break;
				}
			}

			/* we have found a CRTC, so save it and return */
			if (crtc >= 0) {
				drmModeFreeEncoder(enc);
				dev->crtc = crtc;
				return 0;
			}
		}

		drmModeFreeEncoder(enc);
	}

	fprintf(stderr, "cannot find suitable CRTC for connector %u\n",
		conn->connector_id);
	return -ENOENT;
}

static int modeset_create_fb(int fd, struct modeset_dev *dev)
{
	struct drm_mode_create_dumb creq;
	struct drm_mode_destroy_dumb dreq;
	struct drm_mode_map_dumb mreq;
	int ret;

	/* create dumb buffer */
	memset(&creq, 0, sizeof(creq));
	creq.width = dev->width;
	creq.height = dev->height;
	creq.bpp = 32;
	ret = drmIoctl(fd, DRM_IOCTL_MODE_CREATE_DUMB, &creq);
	if (ret < 0) {
		fprintf(stderr, "cannot create dumb buffer (%d): %m\n",
			errno);
		return -errno;
	}
	dev->stride = creq.pitch;
	dev->size = creq.size;
	dev->handle = creq.handle;

	/* create framebuffer object for the dumb-buffer */
	ret = drmModeAddFB(fd, dev->width, dev->height, 24, 32, dev->stride,
			   dev->handle, &dev->fb);
	if (ret) {
		fprintf(stderr, "cannot create framebuffer (%d): %m\n",
			errno);
		ret = -errno;
		goto err_destroy;
	}

	/* prepare buffer for memory mapping */
	memset(&mreq, 0, sizeof(mreq));
	mreq.handle = dev->handle;
	ret = drmIoctl(fd, DRM_IOCTL_MODE_MAP_DUMB, &mreq);
	if (ret) {
		fprintf(stderr, "cannot map dumb buffer (%d): %m\n",
			errno);
		ret = -errno;
		goto err_fb;
	}

	/* perform actual memory mapping */
	dev->map = mmap(0, dev->size, PROT_READ | PROT_WRITE, MAP_SHARED,
		        fd, mreq.offset);
	if (dev->map == MAP_FAILED) {
		//fprintf(stderr, "cannot mmap dumb buffer (%d): %m\n",
		//	errno);
		//ret = -errno;
		//goto err_fb;
		dev->map = NULL;
	} else {
	  /* clear the framebuffer to 0 */
	  memset(dev->map, 0, dev->size);
	}

	return 0;

err_fb:
	drmModeRmFB(fd, dev->fb);
err_destroy:
	memset(&dreq, 0, sizeof(dreq));
	dreq.handle = dev->handle;
	drmIoctl(fd, DRM_IOCTL_MODE_DESTROY_DUMB, &dreq);
	return ret;
}

static int modeset_setup_dev(int fd, drmModeRes *res, drmModeConnector *conn,
			     struct modeset_dev *dev)
{
	int ret;

	/* check if a monitor is connected */
	if (conn->connection != DRM_MODE_CONNECTED) {
		fprintf(stderr, "ignoring unused connector %u\n",
			conn->connector_id);
		return -ENOENT;
	}

	/* check if there is at least one valid mode */
	if (conn->count_modes == 0) {
		fprintf(stderr, "no valid mode for connector %u\n",
			conn->connector_id);
		return -EFAULT;
	}

	/* copy the mode information into our device structure */
	memcpy(&dev->mode, &conn->modes[0], sizeof(dev->mode));
	dev->width = conn->modes[0].hdisplay;
	dev->height = conn->modes[0].vdisplay;
	//fprintf(stderr, "mode for connector %u is %ux%u\n",
	//	conn->connector_id, dev->width, dev->height);

	/* find a crtc for this connector */
	ret = modeset_find_crtc(fd, res, conn, dev);
	if (ret) {
		fprintf(stderr, "no valid crtc for connector %u\n",
			conn->connector_id);
		return ret;
	}

	/* create a framebuffer for this CRTC */
	ret = modeset_create_fb(fd, dev);
	if (ret) {
		fprintf(stderr, "cannot create framebuffer for connector %u\n",
			conn->connector_id);
		return ret;
	}

	return 0;
}

static int crtc_cmp(drmModeModeInfo *a, drmModeModeInfo *b) {
  if(a->clock       == b->clock       &&
     a->hdisplay    == b->hdisplay    &&
     a->hsync_start == b->hsync_start &&
     a->hsync_end   == b->hsync_end   &&
     a->htotal      == b->htotal      &&
     a->hskew       == b->hskew       &&
     a->vdisplay    == b->vdisplay    &&
     a->vsync_start == b->vsync_start &&
     a->vsync_end   == b->vsync_end   &&
     a->vtotal      == b->vtotal      &&
     a->vscan       == b->vscan       &&
     a->vrefresh    == b->vrefresh    &&
     a->flags 	    == b->flags       &&
     a->type  	    == b->type) {

    if(a->name == NULL && b == NULL) return  0;
    if(a->name == NULL || b == NULL) return -1;
    if(strcmp(a->name, b->name) == 0) {
      return 0;
    }
  }
  return -1;
}

// batocera : must return a single word for parsing by batocera-resolution.drm
static char* conntype2str(uint32_t type) {
  if(type == DRM_MODE_CONNECTOR_VGA)  	     return "VGA";
  if(type == DRM_MODE_CONNECTOR_DVII) 	     return "DVII";
  if(type == DRM_MODE_CONNECTOR_DVID) 	     return "DVID";
  if(type == DRM_MODE_CONNECTOR_DVIA) 	     return "DVIA";
  if(type == DRM_MODE_CONNECTOR_Composite)   return "COMPOSITE";
  if(type == DRM_MODE_CONNECTOR_SVIDEO)      return "SVIDEO";
  if(type == DRM_MODE_CONNECTOR_LVDS)        return "LVDS";
  if(type == DRM_MODE_CONNECTOR_Component)   return "COMPONENT";
  if(type == DRM_MODE_CONNECTOR_9PinDIN)     return "9PINDIN";
  if(type == DRM_MODE_CONNECTOR_DisplayPort) return "DISPLAYPORT";
  if(type == DRM_MODE_CONNECTOR_HDMIA) 	     return "HDMIA";
  if(type == DRM_MODE_CONNECTOR_HDMIB) 	     return "HDMIB";
  if(type == DRM_MODE_CONNECTOR_TV)    	     return "TV";
  if(type == DRM_MODE_CONNECTOR_eDP)   	     return "EDP";
  if(type == DRM_MODE_CONNECTOR_VIRTUAL)     return "VIRTUAL";
  if(type == DRM_MODE_CONNECTOR_DSI) 	     return "DSI";
#ifndef HAVE_NOT_DRM_MODE_CONNECTOR_DPI
  if(type == DRM_MODE_CONNECTOR_DPI) 	     return "DPI";
#endif
  //if(type == DRM_MODE_CONNECTOR_WRITEBACK)   return "WRITEBACK";
  //if(type == DRM_MODE_CONNECTOR_SPI)         return "SPI";
  return "OUTPUT"; // unknown
}

static int modeset_prepare(int fd, int do_current)
{
	drmModeRes *res;
	drmModeConnector *conn;
	unsigned int i, j;
	struct modeset_dev *dev;
	int ret;
	drmModeCrtc *live_crtc;
	char* connType;

	/* retrieve resources */
	res = drmModeGetResources(fd);
	if (!res) {
		fprintf(stderr, "cannot retrieve DRM resources (%d): %m\n",
			errno);
		return -errno;
	}

	/* iterate all connectors */
	for (i = 0; i < res->count_connectors; ++i) {
		/* get information for each connector */
		conn = drmModeGetConnector(fd, res->connectors[i]);
		if (!conn) {
			fprintf(stderr, "cannot retrieve DRM connector %u:%u (%d): %m\n",
				i, res->connectors[i], errno);
			continue;
		}

		if(conn->connection == DRM_MODE_DISCONNECTED) {
		  connType = conntype2str(conn->connector_type);
		  fprintf(stderr, "connector %s disconnected\n", connType);
		  continue;
		}

		/* create a device structure */
		dev = malloc(sizeof(*dev));
		memset(dev, 0, sizeof(*dev));
		dev->conn = conn->connector_id;

		/* call helper function to prepare this connector */
		ret = modeset_setup_dev(fd, res, conn, dev);
		if (ret) {
			if (ret != -ENOENT) {
				errno = -ret;
				fprintf(stderr, "cannot setup device for connector %u:%u (%d): %m\n",
					i, res->connectors[i], errno);
			}
			free(dev);
			drmModeFreeConnector(conn);
			continue;
		}

		// batocera
		connType = conntype2str(conn->connector_type);

		if(do_current == 1) {
		  live_crtc = drmModeGetCrtc(fd, dev->crtc);
		  for (j = 0; (int)j < conn->count_modes; j++) {
		    if(crtc_cmp(&live_crtc->mode, conn->modes+j) == 0) {
		      if(!(conn->modes[j].hdisplay == 1366 && conn->modes[j].vdisplay == 768))
		      printf("%d.%d:%s %dx%d %uHz (%s%s)\n",
			     i, j,
			     connType,
			     conn->modes[j].hdisplay,
			     conn->modes[j].vdisplay,
			     conn->modes[j].vrefresh,
			     conn->modes[j].name,
			     (conn->modes[j].type & DRM_MODE_TYPE_PREFERRED) == 0 ? "" : "*");
		    }
		  }
		}

		if(do_current == 0) {
		  for (j = 0; (int)j < conn->count_modes; j++) {
		    if(!(conn->modes[j].hdisplay == 1366 && conn->modes[j].vdisplay == 768))
		    printf("%d.%d:%s %dx%d %uHz (%s%s)\n",
			   i, j,
			   connType,
			   conn->modes[j].hdisplay,
			   conn->modes[j].vdisplay,
			   conn->modes[j].vrefresh,
			   conn->modes[j].name,
			   (conn->modes[j].type & DRM_MODE_TYPE_PREFERRED) == 0 ? "" : "*");
		  }
		}
		

		/* free connector data and link device into global list */
		drmModeFreeConnector(conn);
		dev->next = modeset_list;
		modeset_list = dev;
	}

	/* free resources again */
	drmModeFreeResources(res);
	return 0;
}

static int modeset_open(int *out, const char *node)
{
	int fd, ret;
	uint64_t has_dumb;

	fd = open(node, O_RDWR | O_CLOEXEC);
	if (fd < 0) {
		ret = -errno;
		fprintf(stderr, "cannot open '%s': %m\n", node);
		return ret;
	}

	if (drmGetCap(fd, DRM_CAP_DUMB_BUFFER, &has_dumb) < 0 ||
	    !has_dumb) {
		fprintf(stderr, "drm device '%s' does not support dumb buffers\n",
			node);
		close(fd);
		return -EOPNOTSUPP;
	}

	*out = fd;
	return 0;
}

static void modeset_cleanup(int fd)
{
	struct modeset_dev *iter;
	struct drm_mode_destroy_dumb dreq;

	while (modeset_list) {
		/* remove from global list */
		iter = modeset_list;
		modeset_list = iter->next;

		if(iter->map != NULL) {
		  munmap(iter->map, iter->size);
		}
		drmModeRmFB(fd, iter->fb);

		memset(&dreq, 0, sizeof(dreq));
		dreq.handle = iter->handle;
		drmIoctl(fd, DRM_IOCTL_MODE_DESTROY_DUMB, &dreq);

		free(iter);
	}
}

int main(int argc, char **argv)
{
  int ret, fd, i;
  const char *card;
  struct modeset_dev *iter;
  int do_current = 0;

	if (argc > 1)
		card = argv[1];
	else
		card = "/dev/dri/card0";

	if (argc > 2)
	  if(strcmp(argv[2], "current") == 0)
	     do_current = 1;
	fprintf(stderr, "using card '%s'\n", card);

	/* open the DRM device */
	ret = modeset_open(&fd, card);
	if (ret)
		goto out_return;

	/* prepare all connectors and CRTCs */
        ret = modeset_prepare(fd, do_current);
	if (ret)
		goto out_close;

	// main //

	modeset_cleanup(fd);

	ret = 0;

out_close:
	close(fd);
out_return:
	if (ret) {
		errno = -ret;
		fprintf(stderr, "modeset failed with error %d: %m\n", errno);
	}
	return ret;
}
