/*
 *  Copyright (c) 2013	Markus Hiienkari
 *
 *  Based on the db9 driver by Vojtech Pavlik
 */

/*
 * Atari, Amstrad, Commodore, Amiga, Sega, etc. joystick driver for Linux
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
 * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
 *
 * Should you need to contact me, the author, you can do so either by
 * e-mail - mail your message to <vojtech@ucw.cz>, or by paper mail:
 * Vojtech Pavlik, Simunkova 1594, Prague 8, 182 00 Czech Republic
 */

#include <linux/kernel.h>
#include <linux/module.h>
#include <linux/delay.h>
#include <linux/init.h>
#include <linux/input.h>
#include <linux/mutex.h>
#include <linux/slab.h>
#include <asm/io.h>

MODULE_AUTHOR("Markus Hiienkari <mhiienka@niksula.hut.fi>");
MODULE_DESCRIPTION("Atari, Amstrad, Commodore, Amiga, Sega, etc. joystick driver");
MODULE_LICENSE("GPL");

#define DB9_MAX_DEVICES		2

/* GPIO definitions */
static volatile unsigned *gpio;
#define BCM2708_PERI_BASE 0x20000000
#define GPIO_BASE                (BCM2708_PERI_BASE + 0x200000) /* GPIO controller */

#define GPIO_SET *(gpio+7)
#define GPIO_CLR *(gpio+10)

#define GPIO_STATUS (*(gpio+13))

#define INP_GPIO(g) *(gpio+((g)/10)) &= ~(7<<(((g)%10)*3))
#define OUT_GPIO(g) *(gpio+((g)/10)) |=  (1<<(((g)%10)*3))

#define MAX_PORT_GPIO			7

/* Port gpio IDs */
static const unsigned char gpio_id[DB9_MAX_DEVICES][MAX_PORT_GPIO] = { { 4, 7, 8, 9, 10, 11, 14 },
																		{ 15, 17, 18, 22, 23, 24, 25 } };
/* Port status bits */
static const unsigned long psb[DB9_MAX_DEVICES][MAX_PORT_GPIO] = { { 1<<4, 1<<7, 1<<8, 1<<9, 1<<10, 1<<11, 1<<14 },
																{ 1<<15, 1<<17, 1<<18, 1<<22, 1<<23, 1<<24, 1<<25 } };

struct db9_config {
	int args[DB9_MAX_DEVICES];
	unsigned int nargs;
};

static struct db9_config db9_cfg __initdata;

module_param_array_named(map, db9_cfg.args, int, &(db9_cfg.nargs), 0);
MODULE_PARM_DESC(map, "Describes the set of pad connections (<PORT1>,<PORT2>)");

#define DB9_MULTI_STICK		0x01
#define DB9_MULTI2_STICK	0x02
#define DB9_MULTI3_STICK	0x03
#define DB9_GENESIS_PAD		0x04
#define DB9_GENESIS5_PAD	0x05
#define DB9_GENESIS6_PAD	0x06
#define DB9_SATURN_PAD		0x07
#define DB9_CD32_PAD		0x08
#define DB9_MAX_PAD			0x09


/* Button map */
#define DB9_UP			0
#define DB9_DOWN		1
#define DB9_LEFT		2
#define DB9_RIGHT		3
#define DB9_FIRE1		4
#define DB9_FIRE2		5
#define DB9_FIRE3		6
/* Select pins for MD/SAT/CD32 pads */
#define DB9_SELECT0		6
#define DB9_SELECT1		5


#define DB9_GENESIS_DELAY	5
#define DB9_REFRESH_TIME	HZ/100

struct db9_mode_data {
	const char *name;
	const short *buttons;
	int n_buttons;
	int n_axis;
	unsigned gpio_num_inputs; /* number of inputs pins */
	unsigned gpio_num_outputs; /* number of output pins (select lines) */
};

struct db9_pad {
	struct input_dev *dev;
	int mode;
	char phys[32];
};

struct db9 {
	struct db9_pad pads[DB9_MAX_DEVICES];
	struct timer_list timer;
	int used;
	struct mutex mutex;
};

static struct db9 *db9_base;

static const short db9_multi_btn[] = { BTN_TRIGGER, BTN_THUMB, BTN_THUMB2 };
static const short db9_genesis_btn[] = { BTN_START, BTN_A, BTN_B, BTN_C, BTN_X, BTN_Y, BTN_Z, BTN_MODE };
static const short db9_saturn_btn[] = { BTN_A, BTN_B, BTN_C, BTN_X, BTN_Y, BTN_Z, BTN_TL, BTN_TR, BTN_START };
static const short db9_cd32_btn[] = { BTN_A, BTN_B, BTN_X, BTN_Y, BTN_TR, BTN_TL, BTN_START };
static const short db9_abs[] = { ABS_X, ABS_Y, ABS_RX, ABS_RY, ABS_RZ, ABS_Z, ABS_HAT0X, ABS_HAT0Y, ABS_HAT1X, ABS_HAT1Y };

static const struct db9_mode_data db9_modes[] = {
	{ NULL,					 				NULL,		  0,  0,  0,  0 },
	{ "Multisystem joystick",			 db9_multi_btn,	  1,  2,  5,  0 },
	{ "Multisystem joystick (2 fire)",	 db9_multi_btn,	  2,  2,  6,  0 },
	{ "Multisystem joystick (3 fire)",	 db9_multi_btn,	  3,  2,  7,  0 },
	{ "Genesis pad",					 db9_genesis_btn, 4,  2,  6,  1 },
	{ "Genesis 5 pad",					 db9_genesis_btn, 6,  2,  6,  1 },
	{ "Genesis 6 pad",					 db9_genesis_btn, 8,  2,  6,  1 },
	{ "Saturn pad",						 db9_saturn_btn,  9,  7,  4,  2 },
	{ "Amiga CD-32 pad",				 db9_saturn_btn,  7,  2,  5,  2 },
};

/*
 * Saturn controllers
 */
#define DB9_SATURN_DELAY 1
#define DB9_SATURN_ANALOG_DELAY 7
static const int db9_saturn_byte[] = { 1, 1, 1, 2, 2, 2, 2, 2, 1 };
static const unsigned char db9_saturn_mask[] = { 0x04, 0x01, 0x02, 0x40, 0x20, 0x10, 0x08, 0x80, 0x08 };

/*
 * db9_saturn_write_sub() writes 2 bit data.
 */
static void db9_saturn_write_sub(int port, unsigned char data)
{
	if (data & 0x1)
		GPIO_SET = psb[port][DB9_SELECT0];
	else
		GPIO_CLR = psb[port][DB9_SELECT0];
	
	if ((data >> 1) & 0x1)
		GPIO_SET = psb[port][DB9_SELECT1];
	else
		GPIO_CLR = psb[port][DB9_SELECT1];
}

/*
 * db9_saturn_read_sub() reads 4 bit data.
 */
static unsigned char db9_saturn_read_sub(int port)
{
	unsigned long data;

	/* Delay between select and read */
	udelay(DB9_SATURN_DELAY);

	data = GPIO_STATUS;

	return (data & psb[port][DB9_UP] ? 1 : 0) | (data & psb[port][DB9_DOWN] ? 2 : 0)
	     | (data & psb[port][DB9_LEFT] ? 4 : 0) | (data & psb[port][DB9_RIGHT] ? 8 : 0);
}

/*
 * db9_saturn_read_analog() sends clock and reads 8 bit data.
 */
static unsigned char db9_saturn_read_analog(int port)
{
	unsigned char data;

	db9_saturn_write_sub(port, 0);
	udelay(DB9_SATURN_ANALOG_DELAY);
	data = db9_saturn_read_sub(port) << 4;
	db9_saturn_write_sub(port, 2);
	udelay(DB9_SATURN_ANALOG_DELAY);
	data |= db9_saturn_read_sub(port);
	return data;
}

/*
 * db9_saturn_read_packet() reads whole saturn packet at connector
 * and returns device identifier code.
 */
static unsigned char db9_saturn_read_packet(int port, unsigned char *data)
{
	int i;
	unsigned char tmp;

	db9_saturn_write_sub(port, 3);
	data[0] = db9_saturn_read_sub(port);
	switch (data[0] & 0x0f) {
	case 0xf:
		/* 1111  no pad */
		return data[0] = 0xff;
	case 0x4: case 0x4 | 0x8:
		/* ?100 : digital controller */
		db9_saturn_write_sub(port, 0);
		data[2] = db9_saturn_read_sub(port) << 4;
		db9_saturn_write_sub(port, 2);
		data[1] = db9_saturn_read_sub(port) << 4;
		db9_saturn_write_sub(port, 1);
		data[1] |= db9_saturn_read_sub(port);
		db9_saturn_write_sub(port, 3);
		/* data[2] |= db9_saturn_read_sub(port, type); */
		data[2] |= data[0];
		return data[0] = 0x02;
	case 0x1:
		/* 0001 : analog controller or multitap */
		db9_saturn_write_sub(port, 2);
		udelay(DB9_SATURN_ANALOG_DELAY);
		data[0] = db9_saturn_read_analog(port);
		if (data[0] != 0x41) {
			/* read analog controller */
			for (i = 0; i < (data[0] & 0x0f); i++)
				data[i + 1] = db9_saturn_read_analog(port);
			db9_saturn_write_sub(port, 3);
			return data[0];
		} else {
			/* read multitap NOT SUPPORTED */
			db9_saturn_write_sub(port, 3);
			return data[0] = 0xff;
		}
	case 0x0:
		/* 0000 : mouse */
		db9_saturn_write_sub(port, 2);
		udelay(DB9_SATURN_ANALOG_DELAY);
		tmp = db9_saturn_read_analog(port);
		if (tmp == 0xff) {
			for (i = 0; i < 3; i++)
				data[i + 1] = db9_saturn_read_analog(port);
			db9_saturn_write_sub(port, 3);
			return data[0] = 0xe3;
		}
	default:
		return data[0];
	}
}

/*
 * db9_saturn_report() analyzes packet and reports.
 */
static void db9_saturn_report(unsigned char id, unsigned char *data, struct input_dev *dev)
{
	int i;

	switch (data[0]) {
	case 0x16: /* multi controller (analog 4 axis) */
		input_report_abs(dev, db9_abs[5], data[6]);
	case 0x15: /* mission stick (analog 3 axis) */
		input_report_abs(dev, db9_abs[3], data[4]);
		input_report_abs(dev, db9_abs[4], data[5]);
	case 0x13: /* racing controller (analog 1 axis) */
		input_report_abs(dev, db9_abs[2], data[3]);
	case 0x34: /* saturn keyboard (udlr ZXC ASD QE Esc) */
	case 0x02: /* digital pad (digital 2 axis + buttons) */
		input_report_abs(dev, db9_abs[0], !(data[1] & 128) - !(data[1] & 64));
		input_report_abs(dev, db9_abs[1], !(data[1] & 32) - !(data[1] & 16));
		for (i = 0; i < 9; i++)
			input_report_key(dev, db9_saturn_btn[i], ~data[db9_saturn_byte[i]] & db9_saturn_mask[i]);
		break;
	case 0x19: /* mission stick x2 (analog 6 axis + buttons) */
		input_report_abs(dev, db9_abs[0], !(data[1] & 128) - !(data[1] & 64));
		input_report_abs(dev, db9_abs[1], !(data[1] & 32) - !(data[1] & 16));
		for (i = 0; i < 9; i++)
			input_report_key(dev, db9_saturn_btn[i], ~data[db9_saturn_byte[i]] & db9_saturn_mask[i]);
		input_report_abs(dev, db9_abs[2], data[3]);
		input_report_abs(dev, db9_abs[3], data[4]);
		input_report_abs(dev, db9_abs[4], data[5]);
		/*
		input_report_abs(dev, db9_abs[8], (data[j + 6] & 128 ? 0 : 1) - (data[j + 6] & 64 ? 0 : 1));
		input_report_abs(dev, db9_abs[9], (data[j + 6] & 32 ? 0 : 1) - (data[j + 6] & 16 ? 0 : 1));
		*/
		input_report_abs(dev, db9_abs[6], data[7]);
		input_report_abs(dev, db9_abs[7], data[8]);
		input_report_abs(dev, db9_abs[5], data[9]);
		break;
	case 0xd3: /* sankyo ff (analog 1 axis + stop btn) */
		input_report_key(dev, BTN_A, data[3] & 0x80);
		input_report_abs(dev, db9_abs[2], data[3] & 0x7f);
		break;
	case 0xe3: /* shuttle mouse (analog 2 axis + buttons. signed value) */
		input_report_key(dev, BTN_START, data[1] & 0x08);
		input_report_key(dev, BTN_A, data[1] & 0x04);
		input_report_key(dev, BTN_C, data[1] & 0x02);
		input_report_key(dev, BTN_B, data[1] & 0x01);
		input_report_abs(dev, db9_abs[2], data[2] ^ 0x80);
		input_report_abs(dev, db9_abs[3], (0xff-(data[3] ^ 0x80))+1); /* */
		break;
	case 0xff:
	default: /* no pad */
		input_report_abs(dev, db9_abs[0], 0);
		input_report_abs(dev, db9_abs[1], 0);
		for (i = 0; i < 9; i++)
			input_report_key(dev, db9_saturn_btn[i], 0);
		break;
	}

	return;
}

static void db9_saturn(int port, struct input_dev *dev)
{
	/* Info byte + max. 15 data bytes */
	unsigned char data[16];
	unsigned char id;
	
	id = db9_saturn_read_packet(port, data);
	db9_saturn_report(id, data, dev);

	return;
}

static void db9_timer(unsigned long private)
{
	struct db9 *db9 = (void *) private;
	struct db9_pad *pad;
	struct input_dev *dev;
	int i;
	unsigned long data;

	for (i = 0; i < DB9_MAX_DEVICES; i++) {
		pad = &db9->pads[i];
		dev = pad->dev;

		switch (pad->mode) {
			case DB9_MULTI_STICK:

				data = GPIO_STATUS;

				input_report_abs(dev, ABS_X, (data & psb[i][DB9_RIGHT] ? 0 : 1) - (data & psb[i][DB9_LEFT] ? 0 : 1));
				input_report_abs(dev, ABS_Y, (data & psb[i][DB9_DOWN]  ? 0 : 1) - (data & psb[i][DB9_UP]   ? 0 : 1));
				input_report_key(dev, BTN_TRIGGER, ~data & psb[i][DB9_FIRE1]);
				break;

			case DB9_MULTI2_STICK:

				data = GPIO_STATUS;

				input_report_abs(dev, ABS_X, (data & psb[i][DB9_RIGHT] ? 0 : 1) - (data & psb[i][DB9_LEFT] ? 0 : 1));
				input_report_abs(dev, ABS_Y, (data & psb[i][DB9_DOWN]  ? 0 : 1) - (data & psb[i][DB9_UP]   ? 0 : 1));
				input_report_key(dev, BTN_TRIGGER, ~data & psb[i][DB9_FIRE1]);
				input_report_key(dev, BTN_THUMB,   ~data & psb[i][DB9_FIRE2]);
				break;
				
			case DB9_MULTI3_STICK:

				data = GPIO_STATUS;

				input_report_abs(dev, ABS_X, (data & psb[i][DB9_RIGHT] ? 0 : 1) - (data & psb[i][DB9_LEFT] ? 0 : 1));
				input_report_abs(dev, ABS_Y, (data & psb[i][DB9_DOWN]  ? 0 : 1) - (data & psb[i][DB9_UP]   ? 0 : 1));
				input_report_key(dev, BTN_TRIGGER, ~data & psb[i][DB9_FIRE1]);
				input_report_key(dev, BTN_THUMB,   ~data & psb[i][DB9_FIRE2]);
				input_report_key(dev, BTN_THUMB2,  ~data & psb[i][DB9_FIRE3]);
				break;

			case DB9_GENESIS_PAD:

				GPIO_SET = psb[i][DB9_SELECT0];
				udelay(DB9_GENESIS_DELAY);
				data = GPIO_STATUS;

				input_report_abs(dev, ABS_X, (data & psb[i][DB9_RIGHT] ? 0 : 1) - (data & psb[i][DB9_LEFT] ? 0 : 1));
				input_report_abs(dev, ABS_Y, (data & psb[i][DB9_DOWN]  ? 0 : 1) - (data & psb[i][DB9_UP]   ? 0 : 1));
				input_report_key(dev, BTN_B, ~data & psb[i][DB9_FIRE1]);
				input_report_key(dev, BTN_C, ~data & psb[i][DB9_FIRE2]);

				GPIO_CLR = psb[i][DB9_SELECT0];
				udelay(DB9_GENESIS_DELAY);
				data = GPIO_STATUS;

				input_report_key(dev, BTN_A,     ~data & psb[i][DB9_FIRE1]);
				input_report_key(dev, BTN_START, ~data & psb[i][DB9_FIRE2]);
				break;

			case DB9_GENESIS5_PAD:

				GPIO_SET = psb[i][DB9_SELECT0];
				udelay(DB9_GENESIS_DELAY);
				data = GPIO_STATUS;

				input_report_abs(dev, ABS_X, (data & psb[i][DB9_RIGHT] ? 0 : 1) - (data & psb[i][DB9_LEFT] ? 0 : 1));
				input_report_abs(dev, ABS_Y, (data & psb[i][DB9_DOWN]  ? 0 : 1) - (data & psb[i][DB9_UP]   ? 0 : 1));
				input_report_key(dev, BTN_B, ~data & psb[i][DB9_FIRE1]);
				input_report_key(dev, BTN_C, ~data & psb[i][DB9_FIRE2]);

				GPIO_CLR = psb[i][DB9_SELECT0];
				udelay(DB9_GENESIS_DELAY);
				data = GPIO_STATUS;

				input_report_key(dev, BTN_A,     ~data & psb[i][DB9_FIRE1]);
				input_report_key(dev, BTN_X,     ~data & psb[i][DB9_FIRE2]);
				input_report_key(dev, BTN_Y,     ~data & psb[i][DB9_LEFT]);
				input_report_key(dev, BTN_START, ~data & psb[i][DB9_RIGHT]);
				break;

			case DB9_GENESIS6_PAD:

				GPIO_SET = psb[i][DB9_SELECT0]; /* 1 */
				udelay(DB9_GENESIS_DELAY);
				data = GPIO_STATUS;

				input_report_abs(dev, ABS_X, (data & psb[i][DB9_RIGHT] ? 0 : 1) - (data & psb[i][DB9_LEFT] ? 0 : 1));
				input_report_abs(dev, ABS_Y, (data & psb[i][DB9_DOWN]  ? 0 : 1) - (data & psb[i][DB9_UP]   ? 0 : 1));
				input_report_key(dev, BTN_B, ~data & psb[i][DB9_FIRE1]);
				input_report_key(dev, BTN_C, ~data & psb[i][DB9_FIRE2]);

				GPIO_CLR = psb[i][DB9_SELECT0]; /* 2 */
				udelay(DB9_GENESIS_DELAY);
				data = GPIO_STATUS;

				input_report_key(dev, BTN_A, ~data & psb[i][DB9_FIRE1]);
				input_report_key(dev, BTN_START, ~data & psb[i][DB9_FIRE2]);

				GPIO_SET = psb[i][DB9_SELECT0]; /* 3 */
				udelay(DB9_GENESIS_DELAY);
				GPIO_CLR = psb[i][DB9_SELECT0]; /* 4 */
				udelay(DB9_GENESIS_DELAY);
				GPIO_SET = psb[i][DB9_SELECT0]; /* 5 */
				udelay(DB9_GENESIS_DELAY);
				data = GPIO_STATUS;

				input_report_key(dev, BTN_X,    ~data & psb[i][DB9_LEFT]);
				input_report_key(dev, BTN_Y,    ~data & psb[i][DB9_DOWN]);
				input_report_key(dev, BTN_Z,    ~data & psb[i][DB9_UP]);
				input_report_key(dev, BTN_MODE, ~data & psb[i][DB9_RIGHT]);

				GPIO_CLR = psb[i][DB9_SELECT0]; /* 6 */
				udelay(DB9_GENESIS_DELAY);
				GPIO_SET = psb[i][DB9_SELECT0]; /* 7 */
				udelay(DB9_GENESIS_DELAY);
				GPIO_CLR = psb[i][DB9_SELECT0]; /* 8 */
				break;

			case DB9_SATURN_PAD:

				db9_saturn(i, dev);
				break;

			case DB9_CD32_PAD:

				/* read d-pad */
				data = GPIO_STATUS;
				input_report_abs(dev, ABS_X, (data & psb[i][DB9_RIGHT] ? 0 : 1) - (data & psb[i][DB9_LEFT] ? 0 : 1));
				input_report_abs(dev, ABS_Y, (data & psb[i][DB9_DOWN]  ? 0 : 1) - (data & psb[i][DB9_UP]   ? 0 : 1));

				/* switch to LOAD */
				GPIO_SET = psb[i][DB9_SELECT0];
				udelay(5);

				/* switch to SHIFT */
				GPIO_CLR = psb[i][DB9_SELECT0];
				udelay(5);

				/* read button and shift */
				for (i = 0; i < 7; i++) {
					data = GPIO_STATUS;
					input_report_key(dev, db9_cd32_btn[i], ~data & psb[i][DB9_FIRE1]);
					GPIO_CLR = psb[i][DB9_SELECT1];
					udelay(1);
					GPIO_SET = psb[i][DB9_SELECT1];
					udelay(1);
				}
				break;

			default:
				break;
			}

		if (dev)
			input_sync(dev);
	}

	mod_timer(&db9->timer, jiffies + DB9_REFRESH_TIME);
}

static int db9_open(struct input_dev *dev)
{
	struct db9 *db9 = input_get_drvdata(dev);
	int err;

	err = mutex_lock_interruptible(&db9->mutex);
	if (err)
		return err;

	if (!db9->used++)
		mod_timer(&db9->timer, jiffies + DB9_REFRESH_TIME);

	mutex_unlock(&db9->mutex);
	return 0;
}

static void db9_close(struct input_dev *dev)
{
	struct db9 *db9 = input_get_drvdata(dev);

	mutex_lock(&db9->mutex);
	if (!--db9->used)
		del_timer_sync(&db9->timer);

	mutex_unlock(&db9->mutex);
}

static int __init db9_setup_pad(struct db9 *db9, int idx, int mode)
{
	struct db9_pad *pad = &db9->pads[idx];
	const struct db9_mode_data *db9_mode;
	struct input_dev *input_dev;
	int i, j;
	int err;
	unsigned long gpio_pu_vec = 0;

	if (mode < 1 || mode >= DB9_MAX_PAD || !db9_modes[mode].n_buttons) {
		printk(KERN_ERR "db9.c: Bad device type %d\n", mode);
		return -EINVAL;
	}
	
	db9_mode = &db9_modes[mode];

	pad->dev = input_dev = input_allocate_device();
	if (!input_dev) {
		pr_err("Not enough memory for input device\n");
		return -ENOMEM;
	}

	pad->mode = mode;

	snprintf(pad->phys, sizeof(pad->phys),
			 "input%d", idx);

	input_dev->name = db9_mode->name;
	input_dev->phys = pad->phys;
	input_dev->id.bustype = BUS_VIRTUAL;
	input_dev->id.vendor = 0x0002;
	input_dev->id.product = mode;
	input_dev->id.version = 0x0100;
	
	input_set_drvdata(input_dev, db9);

	input_dev->open = db9_open;
	input_dev->close = db9_close;
	
	input_dev->evbit[0] = BIT_MASK(EV_KEY) | BIT_MASK(EV_ABS);
	for (j = 0; j < db9_mode->n_buttons; j++)
		set_bit(db9_mode->buttons[j], input_dev->keybit);
	for (j = 0; j < db9_mode->n_axis; j++) {
		if (j < 2)
			input_set_abs_params(input_dev, db9_abs[j], -1, 1, 0, 0);
		else
			input_set_abs_params(input_dev, db9_abs[j], 1, 255, 0, 0);
	}

	err = input_register_device(input_dev);
	if (err)
		goto err_free_dev;
		
	/* Configure GPIO states */
	for (i = 0; i < db9_mode->gpio_num_inputs; i++)
		INP_GPIO(gpio_id[idx][i]);
		
	for (i = 0; i < db9_mode->gpio_num_outputs; i++) {
		INP_GPIO(gpio_id[idx][MAX_PORT_GPIO - 1 - i]);
		OUT_GPIO(gpio_id[idx][MAX_PORT_GPIO - 1 - i]);
	}
	
	/* Activate pull-ups on inputs */
	for (i = 0; i < db9_mode->gpio_num_inputs; i++)
		gpio_pu_vec |= (1 << gpio_id[idx][i]);

	*(gpio+37) = 0x02;
	udelay(10);
	*(gpio+38) = gpio_pu_vec;
	udelay(10);
	*(gpio+37) = 0x00;
	*(gpio+38) = 0x00;
	
	printk("PORT%d configured for %s\n", idx + 1, db9_mode->name);

	return 0;

err_free_dev:
	input_free_device(pad->dev);
	pad->dev = NULL;
	return err;
}

static struct db9 __init *db9_probe(int *pads, int n_pads)
{
	struct db9 *db9;
	int i;
	int count = 0;
	int err;

	db9 = kzalloc(sizeof(struct db9), GFP_KERNEL);
	if (!db9) {
		printk(KERN_ERR "db9.c: Not enough memory\n");
		err = -ENOMEM;
		goto err_out;
	}

	mutex_init(&db9->mutex);
	setup_timer(&db9->timer, db9_timer, (long) db9);

	for (i = 0; i < n_pads && i < DB9_MAX_DEVICES; i++) {
		if (!pads[i])
			continue;

		err = db9_setup_pad(db9, i, pads[i]);
		if (err)
			goto err_unreg_devs;

		count++;
	}

	if (count == 0) {
		pr_err("No valid devices specified\n");
		err = -EINVAL;
		goto err_free_db9;
	}
	
	return db9;

err_unreg_devs:
	while (--i >= 0)
		if (db9->pads[i].dev)
			input_unregister_device(db9->pads[i].dev);
 err_free_db9:
	kfree(db9);
 err_out:
	return ERR_PTR(err);
}

static void db9_remove(struct db9 *db9)
{
	const struct db9_mode_data *db9_mode;
	unsigned long gpio_pu_vec = 0;
	int i, j;

	for (i = 0; i < DB9_MAX_DEVICES; i++) {
		if (db9->pads[i].dev)
			input_unregister_device(db9->pads[i].dev);

		if (db9->pads[i].mode) {
 			db9_mode = &db9_modes[db9->pads[i].mode];

			/* Disable pull-ups on inputs */
			for (j = 0; j < db9_mode->gpio_num_inputs; j++)
				gpio_pu_vec |= (1 << gpio_id[i][j]);

			*(gpio+37) = 0x00;
			udelay(10);
			*(gpio+38) = gpio_pu_vec;
			udelay(10);
			*(gpio+37) = 0x00;
			*(gpio+38) = 0x00;

			/* Reset GPIO outputs to inputs */
			for (j = 0; j < db9_mode->gpio_num_outputs; j++)
				INP_GPIO(gpio_id[i][MAX_PORT_GPIO - 1 - j]);
		}
	}

	kfree(db9);
}

static int __init db9_init(void)
{
	/* Set up gpio pointer for direct register access */
   	if ((gpio = ioremap(GPIO_BASE, 0xB0)) == NULL) {
   	   	pr_err("io remap failed\n");
   	   	return -EBUSY;
   	}   	

	if (db9_cfg.nargs < 1) {
		pr_err("at least one device must be specified\n");
		return -EINVAL;
	} else {
		db9_base = db9_probe(db9_cfg.args, db9_cfg.nargs);
		if (IS_ERR(db9_base))
			return -ENODEV;
	}

	return 0;
}

static void __exit db9_exit(void)
{
	if (db9_base)
		db9_remove(db9_base);
			
	iounmap(gpio);
}

module_init(db9_init);
module_exit(db9_exit);
