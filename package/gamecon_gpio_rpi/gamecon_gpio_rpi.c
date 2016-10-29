/*
 * NES, SNES, N64, PSX, Gamecube gamepad driver for Raspberry Pi
 *
 *  Copyright (c) 2012	Markus Hiienkari
 *
 *  Based on the gamecon driver by Vojtech Pavlik
 *  Nes Fourscore support added by Christian Isaksson
 */

/*
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 * 
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 * 
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
 * MA 02110-1301, USA.
 */

#define pr_fmt(fmt) KBUILD_MODNAME ": " fmt

#include <linux/kernel.h>
#include <linux/delay.h>
#include <linux/module.h>
#include <linux/init.h>
#include <linux/input.h>
#include <linux/mutex.h>
#include <linux/slab.h>

#include <linux/ioport.h>
#include <asm/io.h>
#include <mach/platform.h>

MODULE_AUTHOR("Markus Hiienkari");
MODULE_DESCRIPTION("NES, SNES, N64, PSX, GC gamepad driver");
MODULE_LICENSE("GPL");

#define GC_MAX_DEVICES		6

#define GPIO_BASE                (BCM2708_PERI_BASE + 0x200000) /* GPIO controller */

#define GPIO_SET *(gpio+7)
#define GPIO_CLR *(gpio+10)

static volatile unsigned *gpio;

struct gc_config {
	int args[GC_MAX_DEVICES];
	unsigned int nargs;
};

static struct gc_config gc_cfg __initdata;

module_param_array_named(map, gc_cfg.args, int, &(gc_cfg.nargs), 0);
MODULE_PARM_DESC(map, "Describes the set of pad connections (<GPIO0>,<GPIO1>,<GPIO4>,<GPIO7>,<GPIO2>,<GPIO3>)");

enum gc_type {
	GC_NONE = 0,
	GC_SNES,
	GC_NES,
	GC_GCUBE,
    GC_NESFOURSCORE,
	GC_MULTI2,
	GC_N64,
	GC_PSX,
	GC_DDR,
	GC_SNESMOUSE,
	GC_MAX
};

#define GC_REFRESH_TIME	HZ/100

struct gc_pad {
	struct input_dev *dev;
	enum gc_type type;
	char phys[32];

	struct input_dev *dev2;
	char phys2[32];
	unsigned char player_mode;
};

struct gc_nin_gpio {
	unsigned pad_id;
	unsigned cmd_setinputs;
	unsigned cmd_setoutputs;
	unsigned valid_bits;
	unsigned request;
	unsigned request_len;
	unsigned response_len;
	unsigned response_bufsize;
};

struct gc {
	struct gc_pad pads[GC_MAX_DEVICES];
	struct timer_list timer;
	int pad_count[GC_MAX];
	int used;
	struct mutex mutex;
};

struct gc_subdev {
	unsigned int idx;
};

static struct gc *gc_base;

/* GPIO pins 0, 1, 4, 7, 2, 3 */
static const int gc_status_bit[] = { 0x01, 0x02, 0x10, 0x80, 0x04, 0x08 };
static const int gc_gpio_ids[] = { 0, 1, 4, 7, 2, 3 };

static const char *gc_names[] = {
	NULL, "SNES pad", "NES pad", "Gamecube controller", "NES pad (Four Score)",
	"Multisystem 2-button joystick", "N64 controller", "PSX controller",
	"PSX DDR controller", "SNES mouse"
};

/*
 * N64 support.
 */

static const unsigned char gc_n64_bytes[] = { 0, 1, 13, 15, 14, 12, 10, 11, 2, 3 };
static const short gc_n64_btn[] = {
	BTN_A, BTN_B, BTN_C, BTN_X, BTN_Y, BTN_Z,
	BTN_TL, BTN_TR, BTN_TRIGGER, BTN_START
};

#define GC_N64_REQUEST_LENGTH   8               /* transmit request sequence is 8 bits long (without stop bit) */
#define GC_N64_REQUEST          0x80U		 	/* the request data command */

#define GC_N64_LENGTH			33				/* N64 response length, including stop bit */

/* buffer for samples read from pad */
#define GC_N64_BUFSIZE		100*GC_N64_LENGTH

struct gc_nin_gpio n64_prop = { GC_N64,
								0,
								0,
								0,
								GC_N64_REQUEST,
								GC_N64_REQUEST_LENGTH,
								GC_N64_LENGTH,
								GC_N64_BUFSIZE };

/* Send encoded command */
static inline void gc_n64_send_command(struct gc_nin_gpio *ningpio)
{
	int i;
	
	/* set correct GPIOs to outputs */
	*gpio &= ~ningpio->cmd_setinputs;
	*gpio |= ningpio->cmd_setoutputs;
	
	/* transmit a data request to pads */
	for (i = 0; i < ningpio->request_len; i++) {
		if ((unsigned)((ningpio->request >> i) & 1) == 0) {
			GPIO_CLR = ningpio->valid_bits;
			udelay(3);
			GPIO_SET = ningpio->valid_bits;
			udelay(1);
		} else {
			GPIO_CLR = ningpio->valid_bits;
			udelay(1);
			GPIO_SET = ningpio->valid_bits;
			udelay(3);
		}
	}
	
	/* send stop bit (let pull-up handle the last 2us)*/
	GPIO_CLR = ningpio->valid_bits;
	udelay(1);
	GPIO_SET = ningpio->valid_bits;
	
	/* set the GPIOs back to inputs */
	*gpio &= ~ningpio->cmd_setinputs;
}

/*
 * gc_n64_read_packet() reads N64 or Gamecube packet.
 * Each pad uses one bit per byte. So all pads connected to this port
 * are read in parallel.
 */

static void gc_n64_read_packet(struct gc *gc, struct gc_nin_gpio *ningpio, unsigned char *data)
{
	int i,j,k;
	unsigned prev, mindiff=1000, maxdiff=0;
	unsigned long flags;
	static unsigned char samplebuf[6500]; // =max(GC_N64_BUFSIZE, GC_GCUBE_BUFSIZE)
	
	/* disable interrupts */
	local_irq_save(flags);

	gc_n64_send_command(ningpio);
	
	/* start sampling data */
	for (i = 0; i < ningpio->response_bufsize; i++)
		samplebuf[i] = *(gpio+13) & ningpio->valid_bits;
	
	/* enable interrupts when done */
	local_irq_restore(flags);
	
	memset(data, 0x00, ningpio->response_len);

	/* extract correct bit sequence (for each pad) from sampled data */
	for (k = 0; k < GC_MAX_DEVICES; k++) {
		if (gc->pads[k].type != ningpio->pad_id)
			continue;

		/* locate first falling edge */
		for (i = 0; i < ningpio->response_bufsize; i++) {
			if ((samplebuf[i] & gc_status_bit[k]) == 0)
				break;
		}
		
		prev = i;
		j = 0;
		
		while (j < ningpio->response_len-1 && i < ningpio->response_bufsize-1) {
			i++;
			/* detect consecutive falling edges */
			if ((samplebuf[i-1] & gc_status_bit[k]) != 0 && (samplebuf[i] & gc_status_bit[k]) == 0) {
				/* update min&max diffs */
				if (i-prev > maxdiff)
					maxdiff = i - prev;
				if (i-prev < mindiff)
					mindiff = i - prev;

				/* data is taken between 2 falling edges */
				data[j] |= samplebuf[prev+((i-prev)/2)] & gc_status_bit[k];
				j++;
				prev = i;
			}
		}
		
		/* ignore the real stop-bit as it seems to be 0 at times. Invalidate
		 * the read manually instead, if either of the following is true:
		 * 		1. Less than response_len-1 bits read detected from samplebuf
		 * 		2. Variation in falling edge intervals is too high */
		if ((j == ningpio->response_len-1) && (maxdiff < 2*mindiff))
			data[ningpio->response_len-1] |= gc_status_bit[k];
	}
}

static void gc_n64_process_packet(struct gc *gc)
{
	unsigned char data[GC_N64_LENGTH];
	struct input_dev *dev;
	int i, j, s;
	signed char x, y;

	gc_n64_read_packet(gc, &n64_prop, data);

	for (i = 0; i < GC_MAX_DEVICES; i++) {

		if (gc->pads[i].type != GC_N64)
			continue;

		dev = gc->pads[i].dev;
		s = gc_status_bit[i];

		/* ensure that the response is valid */
		if (s & ~(data[8] | data[9] | ~data[32])) {

			x = y = 0;

			for (j = 0; j < 8; j++) {
				if (data[23 - j] & s)
					x |= 1 << j;
				if (data[31 - j] & s)
					y |= 1 << j;
			}

			input_report_abs(dev, ABS_X,  x);
			input_report_abs(dev, ABS_Y, -y);

			input_report_abs(dev, ABS_HAT0X,
					 !(s & data[6]) - !(s & data[7]));
			input_report_abs(dev, ABS_HAT0Y,
					 !(s & data[4]) - !(s & data[5]));

			for (j = 0; j < 10; j++)
				input_report_key(dev, gc_n64_btn[j],
						 s & data[gc_n64_bytes[j]]);

			input_sync(dev);
		}
	}
}

#if 0
static int gc_n64_play_effect(struct input_dev *dev, void *data,
			      struct ff_effect *effect)
{
	return 0;
}

static int __init gc_n64_init_ff(struct input_dev *dev, int i)
{
	struct gc_subdev *sdev;
	int err;

	sdev = kmalloc(sizeof(*sdev), GFP_KERNEL);
	if (!sdev)
		return -ENOMEM;

	sdev->idx = i;

	input_set_capability(dev, EV_FF, FF_RUMBLE);

	err = input_ff_create_memless(dev, sdev, gc_n64_play_effect);
	if (err) {
		kfree(sdev);
		return err;
	}

	return 0;
}
#endif


/*
 * Gamecube support.
 */

static const unsigned char gc_gcube_bytes[] = { 7, 6, 5, 4, 11, 9, 10, 3 };
static const short gc_gcube_btn[] = {
	BTN_A, BTN_B, BTN_X, BTN_Y, BTN_Z,
	BTN_TL, BTN_TR, BTN_START
};

#define GC_GCUBE_REQUEST_LENGTH   24            /* transmit request sequence is 24 bits long (without stop bit) */
#define GC_GCUBE_REQUEST          0x40c002U 	/* the request data command */

#define GC_GCUBE_LENGTH			  65			/* Gamecube response length, including stop bit */

/* buffer for samples read from pad */
#define GC_GCUBE_BUFSIZE		100*GC_GCUBE_LENGTH

struct gc_nin_gpio gcube_prop = { GC_GCUBE,
								0,
								0,
								0,
								GC_GCUBE_REQUEST,
								GC_GCUBE_REQUEST_LENGTH,
								GC_GCUBE_LENGTH,
								GC_GCUBE_BUFSIZE };

static void gc_gcube_process_packet(struct gc *gc)
{
	unsigned char data[GC_GCUBE_LENGTH];
	struct input_dev *dev;
	int i, j, s;
	unsigned char x, y, x2, y2, y3, y4;

	gc_n64_read_packet(gc, &gcube_prop, data);

	for (i = 0; i < GC_MAX_DEVICES; i++) {

		if (gc->pads[i].type != GC_GCUBE)
			continue;

		dev = gc->pads[i].dev;
		s = gc_status_bit[i];

		/* ensure that the response is valid */
		if (s & ~(data[0] | data[1] | ~data[8] | ~data[64])) {

			x = y = x2 = y2 = y3 = y4 = 0;

			for (j = 0; j < 8; j++) {
				if (data[23 - j] & s)
					x |= 1 << j;
				if (data[31 - j] & s)
					y |= 1 << j;
				if (data[39 - j] & s)
					x2 |= 1 << j;
				if (data[47 - j] & s)
					y2 |= 1 << j;
				if (data[55 - j] & s)
					y3 |= 1 << j;
				if (data[63 - j] & s)
					y4 |= 1 << j;					
			}

			input_report_abs(dev, ABS_X, x);
			input_report_abs(dev, ABS_Y, 0xff - y);
			input_report_abs(dev, ABS_RX, x2);
			input_report_abs(dev, ABS_RY, 0xff - y2);
			input_report_abs(dev, ABS_GAS, y3);
			input_report_abs(dev, ABS_BRAKE, y4);			
			
			input_report_abs(dev, ABS_HAT0X,
					 !(s & data[15]) - !(s & data[14]));
			input_report_abs(dev, ABS_HAT0Y,
					 !(s & data[12]) - !(s & data[13]));

			for (j = 0; j < 8; j++)
				input_report_key(dev, gc_gcube_btn[j],
						 s & data[gc_gcube_bytes[j]]);

			input_sync(dev);
		}
	}
}


/*
 * NES/SNES support.
 */

#define GC_NES_DELAY		6	/* Delay between bits - 6us */
#define GC_NES_LENGTH		8	/* The NES pads use 8 bits of data */
#define GC_SNES_LENGTH		12	/* The SNES true length is 16, but the
					   last 4 bits are unused */
#define GC_SNESMOUSE_LENGTH	32	/* The SNES mouse uses 32 bits, the first
					   16 bits are equivalent to a gamepad */
#define GC_NESFOURSCORE_LENGTH	24 /* The NES Four Score adapter uses 24
					   bits of data */

/* clock = gpio10, latch = gpio11 */
#define GC_NES_CLOCK	0x400
#define GC_NES_LATCH	0x800

static const unsigned char gc_nes_bytes[] = { 0, 1, 2, 3 };
static const unsigned char gc_snes_bytes[] = { 8, 0, 2, 3, 9, 1, 10, 11 };
static const short gc_snes_btn[] = {
	BTN_A, BTN_B, BTN_SELECT, BTN_START, BTN_X, BTN_Y, BTN_TL, BTN_TR
};

/*
 * gc_nes_read_packet() reads a NES/SNES packet.
 * Each pad uses one bit per byte. So all pads connected to
 * this port are read in parallel.
 */

static void gc_nes_read_packet(struct gc *gc, int length, unsigned char *data)
{
	int i;

	GPIO_SET = GC_NES_CLOCK | GC_NES_LATCH;
	udelay(GC_NES_DELAY * 2);
	GPIO_CLR = GC_NES_LATCH;

	for (i = 0; i < length; i++) {
		udelay(GC_NES_DELAY);
		GPIO_CLR = GC_NES_CLOCK;
		data[i] = ~(*(gpio+13));
		udelay(GC_NES_DELAY);
		GPIO_SET = GC_NES_CLOCK;
	}
}

static void gc_nes_process_packet(struct gc *gc)
{
	unsigned char data[GC_SNESMOUSE_LENGTH];
	struct gc_pad *pad;
	struct input_dev *dev, *dev2;
	int i, j, s, len;
    unsigned char fs_connected;
	char x_rel, y_rel;

	len = gc->pad_count[GC_SNESMOUSE] ? GC_SNESMOUSE_LENGTH :
			(gc->pad_count[GC_NESFOURSCORE] ? GC_NESFOURSCORE_LENGTH :
			(gc->pad_count[GC_SNES] ? GC_SNES_LENGTH : GC_NES_LENGTH));

	gc_nes_read_packet(gc, len, data);

	for (i = 0; i < GC_MAX_DEVICES; i++) {

		pad = &gc->pads[i];
		dev = pad->dev;
		s = gc_status_bit[i];

		switch (pad->type) {

		case GC_NES:

			input_report_abs(dev, ABS_X, !(s & data[6]) - !(s & data[7]));
			input_report_abs(dev, ABS_Y, !(s & data[4]) - !(s & data[5]));

			for (j = 0; j < 4; j++)
				input_report_key(dev, gc_snes_btn[j],
						 s & data[gc_nes_bytes[j]]);
			input_sync(dev);
			break;

		case GC_SNES:

			input_report_abs(dev, ABS_X, !(s & data[6]) - !(s & data[7]));
			input_report_abs(dev, ABS_Y, !(s & data[4]) - !(s & data[5]));

			for (j = 0; j < 8; j++)
				input_report_key(dev, gc_snes_btn[j],
						 s & data[gc_snes_bytes[j]]);
			input_sync(dev);
			break;

		case GC_SNESMOUSE:
			/*
			 * The 4 unused bits from SNES controllers appear
			 * to be ID bits so use them to make sure we are
			 * dealing with a mouse.
			 * gamepad is connected. This is important since
			 * my SNES gamepad sends 1's for bits 16-31, which
			 * cause the mouse pointer to quickly move to the
			 * upper left corner of the screen.
			 */
			if (!(s & data[12]) && !(s & data[13]) &&
			    !(s & data[14]) && (s & data[15])) {
				input_report_key(dev, BTN_LEFT, s & data[9]);
				input_report_key(dev, BTN_RIGHT, s & data[8]);

				x_rel = y_rel = 0;
				for (j = 0; j < 7; j++) {
					x_rel <<= 1;
					if (data[25 + j] & s)
						x_rel |= 1;

					y_rel <<= 1;
					if (data[17 + j] & s)
						y_rel |= 1;
				}

				if (x_rel) {
					if (data[24] & s)
						x_rel = -x_rel;
					input_report_rel(dev, REL_X, x_rel);
				}

				if (y_rel) {
					if (data[16] & s)
						y_rel = -y_rel;
					input_report_rel(dev, REL_Y, y_rel);
				}

				input_sync(dev);
			}
			break;
				
		case GC_NESFOURSCORE:
			/*
			 * The NES Four Score uses a 24 bit protocol in 4-player mode
			 * 1st 8 bits: controller 1    /    controller 2 (as normal)
			 * 2nd 8 bits: controller 3    /    controller 4 (new ports)
			 * 3rd 8 bits: 0,0,0,1,0,0,0,0 / 0,0,1,0,0,0,0,0 (ID codes)
			 *
			 * The last 8 bits are used to determine if a Four Score
			 * adapter is connected and if the switch is positioned in
			 * 4 player mode.
			 */
			
			dev2 = pad->dev2;
				
			/* Report first byte (first NES pad). */
			input_report_abs(dev, ABS_X, !(s & data[6]) - !(s & data[7]));
			input_report_abs(dev, ABS_Y, !(s & data[4]) - !(s & data[5]));
			
			for (j = 0; j < 4; j++)
				input_report_key(dev, gc_snes_btn[j], s & data[gc_nes_bytes[j]]);
			input_sync(dev);
			
			/* Determine if a NES Four Score ID code is available in the 3rd byte. */
			fs_connected = ( !(s & data[16]) &&	!(s & data[17]) && !(s & data[18]) &&
							  (s & data[19]) &&	!(s & data[20]) && !(s & data[21]) &&
							 !(s & data[22]) &&	!(s & data[23]) ) ||
								( !(s & data[16]) && !(s & data[17]) &&  (s & data[18]) &&
								  !(s & data[19]) && !(s & data[20]) && !(s & data[21]) &&
								  !(s & data[22]) && !(s & data[23]) );
			
			/* Check if the NES Four Score is connected and the toggle switch is set to 4-player mdoe. */
			if(fs_connected) {
				if(pad->player_mode == 2)
					pad->player_mode = 4;
				
				/* Report second byte (second NES pad). */
				input_report_abs(dev2, ABS_X, !(s & data[14]) - !(s & data[15]));
				input_report_abs(dev2, ABS_Y, !(s & data[12]) - !(s & data[13]));
				
				for (j = 0; j < 4; j++) {
					input_report_key(dev2, gc_snes_btn[j], s & data[gc_nes_bytes[j] + 8]);
				}
				input_sync(dev2);
				
			} else if(pad->player_mode == 4) {
				/* Either the toggle switch on the NES Four Score is set to 2-player mode or it is not connected.  */
				pad->player_mode = 2;
				
				/* Clear second NES pad. */
				input_report_abs(dev2, ABS_X, 0);
				input_report_abs(dev2, ABS_Y, 0);
				
				for (j = 0; j < 4; j++) {
					input_report_key(dev2, gc_snes_btn[j], 0);
				}
				input_sync(dev2);
			}
			break;
            
		default:
			break;
		}
	}
}

/*
 * PSX support
 *
 * See documentation at:
 *	http://www.geocities.co.jp/Playtown/2004/psx/ps_eng.txt	
 *	http://www.gamesx.com/controldata/psxcont/psxcont.htm
 *
 */

#define GC_PSX_DELAY	3		/* clock phase length in us. Valid clkfreq is 100kHz...500kHz. 2*udelay(3) results to ~250kHz on RPi1. */
#define GC_PSX_DELAY2	25		/* delay between bytes. */
#define GC_PSX_LENGTH	8		/* talk to the controller in bits */
#define GC_PSX_BYTES	6		/* the maximum number of bytes to read off the controller */

#define GC_PSX_MOUSE	1		/* Mouse */
#define GC_PSX_NEGCON	2		/* NegCon */
#define GC_PSX_NORMAL	4		/* Digital / Analog or Rumble in Digital mode  */
#define GC_PSX_ANALOG	5		/* Analog in Analog mode / Rumble in Green mode */
#define GC_PSX_RUMBLE	7		/* Rumble in Red mode */

#define GC_PSX_CLOCK	(1<<18)		/* Pin 18 */
#define GC_PSX_COMMAND	(1<<14)		/* Pin 14 */
#define GC_PSX_SELECT	(1<<15)		/* Pin 15 */

#define GC_PSX_ID(x)	((x) >> 4)	/* High nibble is device type */
#define GC_PSX_LEN(x)	(((x) & 0xf) << 1)	/* Low nibble is length in bytes/2 */

static const short gc_psx_abs[] = {
	ABS_HAT0X, ABS_HAT0Y, ABS_RX, ABS_RY, ABS_X, ABS_Y
};
static const short gc_psx_btn[] = {
	BTN_TL2, BTN_TR2, BTN_TL, BTN_TR, BTN_X, BTN_A, BTN_B, BTN_Y,
	BTN_SELECT, BTN_THUMBL, BTN_THUMBR, BTN_START
};
static const short gc_psx_ddr_btn[] = { BTN_0, BTN_1, BTN_2, BTN_3 };

/*
 * gc_psx_command() writes 8bit command and reads 8bit data from
 * the psx pad.
 */

static void gc_psx_command(struct gc *gc, int b, unsigned char *data)
{
	int i, j, read;

	memset(data, 0, GC_MAX_DEVICES);

	for (i = 0; i < GC_PSX_LENGTH; i++, b >>= 1) {
		
		GPIO_CLR = GC_PSX_CLOCK;

		if (b & 1)
			GPIO_SET = GC_PSX_COMMAND;
		else
			GPIO_CLR = GC_PSX_COMMAND;
        
		udelay(GC_PSX_DELAY);
        GPIO_SET = GC_PSX_CLOCK;

		read = *(gpio+13);

		for (j = 0; j < GC_MAX_DEVICES; j++) {
			struct gc_pad *pad = &gc->pads[j];

			if (pad->type == GC_PSX || pad->type == GC_DDR)
				data[j] |= (read & gc_status_bit[j]) ? (1 << i) : 0;
		}

		udelay(GC_PSX_DELAY);
	}
    
    udelay(GC_PSX_DELAY2);
}

/*
 * gc_psx_read_packet() reads a whole psx packet and returns
 * device identifier code.
 */

static void gc_psx_read_packet(struct gc *gc,
			       unsigned char data[GC_MAX_DEVICES][GC_PSX_BYTES],
			       unsigned char id[GC_MAX_DEVICES])
{
	int i, j, max_len = 0;
	unsigned long flags;
	unsigned char data2[GC_MAX_DEVICES];

    local_irq_save(flags);

	/* Select pad */
	GPIO_SET = GC_PSX_CLOCK | GC_PSX_SELECT;
    
	/* Deselect, begin command */
	GPIO_CLR = GC_PSX_SELECT;
	udelay(GC_PSX_DELAY2);

	gc_psx_command(gc, 0x01, data2);	/* Access pad */
	gc_psx_command(gc, 0x42, id);		/* Get device ids */
	gc_psx_command(gc, 0, data2);		/* Dump status */

	/* Find the longest pad */
	for (i = 0; i < GC_MAX_DEVICES; i++) {
		struct gc_pad *pad = &gc->pads[i];

		if ((pad->type == GC_PSX || pad->type == GC_DDR) &&
		    GC_PSX_LEN(id[i]) > max_len &&
		    GC_PSX_LEN(id[i]) <= GC_PSX_BYTES) {
			max_len = GC_PSX_LEN(id[i]);
		}
	}

	/* Read in all the data */
	for (i = 0; i < max_len; i++) {
		gc_psx_command(gc, 0, data2);
		for (j = 0; j < GC_MAX_DEVICES; j++)
			data[j][i] = data2[j];
	}

	local_irq_restore(flags);

	GPIO_SET = GC_PSX_CLOCK | GC_PSX_SELECT;

	/* Set id's to the real value */
	for (i = 0; i < GC_MAX_DEVICES; i++)
		id[i] = GC_PSX_ID(id[i]);
}

static void gc_psx_report_one(struct gc_pad *pad, unsigned char psx_type,
			      unsigned char *data)
{
	struct input_dev *dev = pad->dev;
	int i;

	switch (psx_type) {

	case GC_PSX_RUMBLE:

		input_report_key(dev, BTN_THUMBL, ~data[0] & 0x02);
		input_report_key(dev, BTN_THUMBR, ~data[0] & 0x04);

	case GC_PSX_NEGCON:
	case GC_PSX_ANALOG:

		if (pad->type == GC_DDR) {
			for (i = 0; i < 4; i++)
				input_report_key(dev, gc_psx_ddr_btn[i],
						 ~data[0] & (0x10 << i));
		} else {
			for (i = 0; i < 4; i++)
				input_report_abs(dev, gc_psx_abs[i + 2],
						 data[i + 2]);

			input_report_abs(dev, ABS_HAT0X,
				!(data[0] & 0x20) - !(data[0] & 0x80));
			input_report_abs(dev, ABS_HAT0Y,
				!(data[0] & 0x40) - !(data[0] & 0x10));
		}

		for (i = 0; i < 8; i++)
			input_report_key(dev, gc_psx_btn[i], ~data[1] & (1 << i));

		input_report_key(dev, BTN_START,  ~data[0] & 0x08);
		input_report_key(dev, BTN_SELECT, ~data[0] & 0x01);

		input_sync(dev);

		break;

	case GC_PSX_NORMAL:

		if (pad->type == GC_DDR) {
			for (i = 0; i < 4; i++)
				input_report_key(dev, gc_psx_ddr_btn[i],
						 ~data[0] & (0x10 << i));
		} else {
			input_report_abs(dev, ABS_HAT0X,
				!(data[0] & 0x20) - !(data[0] & 0x80));
			input_report_abs(dev, ABS_HAT0Y,
				!(data[0] & 0x40) - !(data[0] & 0x10));

			/*
			 * For some reason if the extra axes are left unset
			 * they drift.
             */
			for (i = 0; i < 4; i++)
                input_report_abs(dev, gc_psx_abs[i + 2], 128);
			 /* This needs to be debugged properly,
			 * maybe fuzz processing needs to be done
			 * in input_sync()
			 *				 --vojtech
			 */
		}

		for (i = 0; i < 8; i++)
			input_report_key(dev, gc_psx_btn[i], ~data[1] & (1 << i));

		input_report_key(dev, BTN_START,  ~data[0] & 0x08);
		input_report_key(dev, BTN_SELECT, ~data[0] & 0x01);

		input_sync(dev);

		break;

	default: /* not a pad, ignore */
		break;
	}
}

static void gc_psx_process_packet(struct gc *gc)
{
	unsigned char data[GC_MAX_DEVICES][GC_PSX_BYTES];
	unsigned char id[GC_MAX_DEVICES];
	struct gc_pad *pad;
	int i;

	gc_psx_read_packet(gc, data, id);

	for (i = 0; i < GC_MAX_DEVICES; i++) {
		pad = &gc->pads[i];
		if (pad->type == GC_PSX || pad->type == GC_DDR)
			gc_psx_report_one(pad, id[i], data[i]);
	}
}

/*
 * gc_timer() initiates reads of console pads data.
 */

static void gc_timer(unsigned long private)
{
	struct gc *gc = (void *) private;

/*
 * N64 & Gamecube pads
 */

	if (gc->pad_count[GC_N64])
		gc_n64_process_packet(gc);
		
	if (gc->pad_count[GC_GCUBE])
		gc_gcube_process_packet(gc);
		
/*
 * NES and SNES pads or mouse
 */

	if (gc->pad_count[GC_NES] ||
	    gc->pad_count[GC_SNES] ||
	    gc->pad_count[GC_SNESMOUSE] ||
		gc->pad_count[GC_NESFOURSCORE]) {
		gc_nes_process_packet(gc);
	}
	
/*
 * PSX controllers
 */

	if (gc->pad_count[GC_PSX] || gc->pad_count[GC_DDR])
		gc_psx_process_packet(gc);

	mod_timer(&gc->timer, jiffies + GC_REFRESH_TIME);
}

static int gc_open(struct input_dev *dev)
{
	struct gc *gc = input_get_drvdata(dev);
	int err;

	err = mutex_lock_interruptible(&gc->mutex);
	if (err)
		return err;

	if (!gc->used++)
		mod_timer(&gc->timer, jiffies + GC_REFRESH_TIME);

	mutex_unlock(&gc->mutex);
	return 0;
}

static void gc_close(struct input_dev *dev)
{
	struct gc *gc = input_get_drvdata(dev);

	mutex_lock(&gc->mutex);
	if (!--gc->used) {
		del_timer_sync(&gc->timer);
	}
	mutex_unlock(&gc->mutex);
}

static int __init gc_setup_pad(struct gc *gc, int idx, int pad_type)
{
	struct gc_pad *pad = &gc->pads[idx];
	struct input_dev *input_dev, *input_dev2;
	int i;
	int err;

	if (pad_type < 1 || pad_type >= GC_MAX) {
		pr_err("Pad type %d unknown\n", pad_type);
		return -EINVAL;
	}

	pad->dev = input_dev = input_allocate_device();
	if (!input_dev) {
		pr_err("Not enough memory for input device\n");
		return -ENOMEM;
	}

	pad->type = pad_type;

	if(pad_type == GC_NESFOURSCORE)
		snprintf(pad->phys, sizeof(pad->phys),
			"input%d_1", idx);
	else
		snprintf(pad->phys, sizeof(pad->phys),
			"input%d", idx);

	input_dev->name = gc_names[pad_type];
	input_dev->phys = pad->phys;
	input_dev->id.bustype = BUS_PARPORT;
	input_dev->id.vendor = 0x0001;
	input_dev->id.product = pad_type;
	input_dev->id.version = 0x0100;

	input_set_drvdata(input_dev, gc);

	input_dev->open = gc_open;
	input_dev->close = gc_close;

	if (pad_type != GC_SNESMOUSE) {
		input_dev->evbit[0] = BIT_MASK(EV_KEY) | BIT_MASK(EV_ABS);

		for (i = 0; i < 2; i++)
			input_set_abs_params(input_dev, ABS_X + i, -1, 1, 0, 0);
	} else
		input_dev->evbit[0] = BIT_MASK(EV_KEY) | BIT_MASK(EV_REL);

	gc->pad_count[pad_type]++;

	switch (pad_type) {

	case GC_N64:
		for (i = 0; i < 10; i++)
			__set_bit(gc_n64_btn[i], input_dev->keybit);

		for (i = 0; i < 2; i++) {
			input_set_abs_params(input_dev, ABS_X + i, -127, 126, 0, 2);
			input_set_abs_params(input_dev, ABS_HAT0X + i, -1, 1, 0, 0);
		}

		/*err = gc_n64_init_ff(input_dev, idx);
		if (err) {
			pr_warning("Failed to initiate rumble for N64 device %d\n", idx);
			goto err_free_dev;
		}*/
		
		/* create bitvectors read/write operations */
		n64_prop.cmd_setinputs |= (7<<(gc_gpio_ids[idx]*3));
		n64_prop.cmd_setoutputs |= (1<<(gc_gpio_ids[idx]*3));
		n64_prop.valid_bits |= gc_status_bit[idx];

		break;
		
	case GC_GCUBE:
		for (i = 0; i < 8; i++)
			__set_bit(gc_gcube_btn[i], input_dev->keybit);

		for (i = 0; i < 2; i++) {
			input_set_abs_params(input_dev, ABS_X + i, 0, 255, 0, 2);
			input_set_abs_params(input_dev, ABS_RX + i, 0, 255, 0, 2);
			input_set_abs_params(input_dev, ABS_GAS + i, 0, 255, 0, 2);
			input_set_abs_params(input_dev, ABS_HAT0X + i, -1, 1, 0, 0);
		}

		/* create bitvectors read/write operations */
		gcube_prop.cmd_setinputs |= (7<<(gc_gpio_ids[idx]*3));
		gcube_prop.cmd_setoutputs |= (1<<(gc_gpio_ids[idx]*3));
		gcube_prop.valid_bits |= gc_status_bit[idx];

		break;
		
	case GC_SNESMOUSE:
		__set_bit(BTN_LEFT, input_dev->keybit);
		__set_bit(BTN_RIGHT, input_dev->keybit);
		__set_bit(REL_X, input_dev->relbit);
		__set_bit(REL_Y, input_dev->relbit);
		break;

	case GC_SNES:
		for (i = 4; i < 8; i++)
			__set_bit(gc_snes_btn[i], input_dev->keybit);
	case GC_NES:
		for (i = 0; i < 4; i++)
			__set_bit(gc_snes_btn[i], input_dev->keybit);
		break;

	case GC_NESFOURSCORE:
        /* Create the extra input_dev generated by the NES Four Score adapter */
        pad->dev2 = input_dev2 = input_allocate_device();
        if (!input_dev2) {
            pr_err("Not enough memory for input device 2\n");
            return -ENOMEM;
        }
        snprintf(pad->phys2, sizeof(pad->phys2), "input%d_2", idx);
        
        input_dev2->name = gc_names[pad_type];
        input_dev2->phys = pad->phys2;
        input_dev2->id.bustype = BUS_PARPORT;
        input_dev2->id.vendor = 0x0001;
        input_dev2->id.product = pad_type;
        input_dev2->id.version = 0x0100;
        
        input_set_drvdata(input_dev2, gc);
        
        input_dev2->open = gc_open;
        input_dev2->close = gc_close;
        
        input_dev2->evbit[0] = BIT_MASK(EV_KEY) | BIT_MASK(EV_ABS);
        
        for (i = 0; i < 2; i++)
            input_set_abs_params(input_dev2, ABS_X + i, -1, 1, 0, 0);
        
        pad->player_mode = 2;
        
        gc->pad_count[pad_type]++;
        
		for (i = 0; i < 4; i++) {
			__set_bit(gc_snes_btn[i], input_dev->keybit);
			__set_bit(gc_snes_btn[i], input_dev2->keybit);
		}
		break;

	case GC_PSX:
        for (i = 0; i < 2; i++)
			input_set_abs_params(input_dev,
					     gc_psx_abs[i], -1, 1, 0, 0);
		for (i = 0; i < 4; i++)
			input_set_abs_params(input_dev,
					     gc_psx_abs[i+2], 0, 255, 0, 28);
		for (i = 0; i < 12; i++)
			__set_bit(gc_psx_btn[i], input_dev->keybit);

		break;

	case GC_DDR:
		for (i = 0; i < 4; i++)
			__set_bit(gc_psx_ddr_btn[i], input_dev->keybit);
		for (i = 0; i < 12; i++)
			__set_bit(gc_psx_btn[i], input_dev->keybit);

		break;
	}

	err = input_register_device(pad->dev);
	if (err)
		goto err_free_dev;
		
	if(pad_type == GC_NESFOURSCORE) {
		err = input_register_device(pad->dev2);
		if(err)
			goto err_free_dev2;
	}

	/* set data pin to input */
	*gpio &= ~(7<<(gc_gpio_ids[idx]*3));
	
	/* enable pull-up on GPIO4 / GPIO7 */
	if ((idx > 1) && (idx < 4)) {
		*(gpio+37) = 0x02;
		udelay(10);
		*(gpio+38) = (1 << gc_gpio_ids[idx]);
		udelay(10);
		*(gpio+37) = 0x00;
		*(gpio+38) = 0x00;
	}
		
	printk("GPIO%d configured for %s data pin\n", gc_gpio_ids[idx], gc_names[pad_type]);

	return 0;

err_free_dev2:
	input_free_device(pad->dev2);
	pad->dev2 = NULL;
err_free_dev:
	input_free_device(pad->dev);
	pad->dev = NULL;
	return err;
}

static struct gc __init *gc_probe(int *pads, int n_pads)
{
	struct gc *gc;
	int i;
	int count = 0;
	int err;

	gc = kzalloc(sizeof(struct gc), GFP_KERNEL);
	if (!gc) {
		pr_err("Not enough memory\n");
		err = -ENOMEM;
		goto err_out;
	}

	mutex_init(&gc->mutex);
	setup_timer(&gc->timer, gc_timer, (long) gc);

	for (i = 0; i < n_pads && i < GC_MAX_DEVICES; i++) {
		if (!pads[i])
			continue;

		err = gc_setup_pad(gc, i, pads[i]);
		if (err)
			goto err_unreg_devs;

		count++;
	}

	if (count == 0) {
		pr_err("No valid devices specified\n");
		err = -EINVAL;
		goto err_free_gc;
	}
	
	/* setup common pins for each pad type */
	if (gc->pad_count[GC_NES] ||
	    gc->pad_count[GC_SNES] ||
	    gc->pad_count[GC_SNESMOUSE] ||
		gc->pad_count[GC_NESFOURSCORE]) {
		
		/* set clk & latch pins to OUTPUT */
		*(gpio+1) &= ~0x3f;
		*(gpio+1) |= 0x09;
	}
	if (gc->pad_count[GC_PSX] ||
		gc->pad_count[GC_DDR]) {
	
		/* set clk, cmd & sel pins to OUTPUT */
		*(gpio+1) &= ~((7<<12) | (7<<15) | (7<<24));
		*(gpio+1) |= ((1<<12) | (1<<15) | (1<<24));
	}

	return gc;

 err_unreg_devs:
	while (--i >= 0) {
		if (gc->pads[i].dev)
			input_unregister_device(gc->pads[i].dev);
		if (gc->pads[i].dev2)
			input_unregister_device(gc->pads[i].dev2);
	}
 err_free_gc:
	kfree(gc);
 err_out:
	return ERR_PTR(err);
}

static void gc_remove(struct gc *gc)
{
	int i;

	for (i = 0; i < GC_MAX_DEVICES; i++) {
		if (gc->pads[i].dev)
			input_unregister_device(gc->pads[i].dev);
		if (gc->pads[i].dev2)
			input_unregister_device(gc->pads[i].dev2);
	}
	kfree(gc);
}

static int __init gc_init(void)
{
	/* Set up gpio pointer for direct register access */
   	if ((gpio = ioremap(GPIO_BASE, 0xB0)) == NULL) {
   	   	pr_err("io remap failed\n");
   	   	return -EBUSY;
   	}   	

	if (gc_cfg.nargs < 1) {
		pr_err("at least one device must be specified\n");
		return -EINVAL;
	} else {
		gc_base = gc_probe(gc_cfg.args, gc_cfg.nargs);
		if (IS_ERR(gc_base))
			return -ENODEV;
	}

	return 0;
}

static void __exit gc_exit(void)
{
	if (gc_base)
		gc_remove(gc_base);
			
	iounmap(gpio);
}

module_init(gc_init);
module_exit(gc_exit);
