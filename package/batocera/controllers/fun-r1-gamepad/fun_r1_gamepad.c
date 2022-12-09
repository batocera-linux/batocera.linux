// SPDX-License-Identifier: GPL-2.0-or-later
/*
 *	Driver for Unico FUN R1 Dual Controllers
 *
 *	Authors:
 *	Cesar Talon <ctalon@gmail.com> [@acmeplus]
 *
 *  v1.0 7/7/2022
 */
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <fcntl.h>
#include <errno.h>
#include <termios.h>
#include <unistd.h>
#include <linux/input.h>
#include <linux/uinput.h>

#define die(str, args...) do { \
        perror(str); \
        exit(EXIT_FAILURE); \
    } while(0)

int debug = 0;

static struct key {
	const char *code;
	int key_code;
	int player;
} keys[] = {
	{"FFFFFFF7", BTN_TL, 1},			// P1 L
	{"7FFFFFFF", BTN_A, 1},				// P1 A
	{"BFFFFFFF", BTN_B, 1},				// P1 B
	{"FFFFFFFD", BTN_TR, 1},			// P1 R
	{"FFFFFFDF", BTN_TL, 2},			// P2 L
	{"DFFFFFFF", BTN_A, 2},				// P2 A
	{"FFFFFFBF", BTN_DPAD_RIGHT, 2},	// P2 RIGHT
	{"FFFFFF7F", BTN_DPAD_LEFT, 2},		// P2 LEFT
	{"FFFFFDFF", BTN_DPAD_UP, 2},		// P2 UP
	{"FFFFFEFF", BTN_DPAD_DOWN, 2},		// P2 DOWN
	{"FFFFFBFF", BTN_START, 2},			// P2 START
	{"00000000", 0x0, 0},				// NC
	{"FFFFFFEF", BTN_TR, 2},			// P2 R
	{"EFFFFFFF", BTN_B, 2},				// P2 B
	{"00000000", 0x0, 0},				// NC
	{"00000000", 0x0, 0},				// NC
	{"00000000", 0x0, 0},				// NC
	{"00000000", 0x0, 0},				// NC
	{"FFFBFFFF", BTN_BACK, 1},			// BACK 
	{"00000000", 0x0, 0},				// NC
	{"00000000", 0x0, 0},				// NC
	{"FFDFFFFF", BTN_START, 1},			// P1 START
	{"FFBFFFFF", BTN_SELECT, 1},		// COIN
	{"FF7FFFFF", BTN_DPAD_UP, 1},		// P1 UP
	{"FEFFFFFF", BTN_DPAD_DOWN, 1},		// P1 DOWN
	{"FDFFFFFF", BTN_DPAD_LEFT, 1},		// P1 LEFT
	{"FBFFFFFF", BTN_DPAD_RIGHT, 1},	// P1 RIGHT
	{"00000000", 0x0, 0},				// NC
	{"FFFFEFFF", BTN_Y, 2},				// P2 Y
	{"FFFFDFFF", BTN_X, 2},				// P2 X
	{"FFFFFFFE", BTN_Y, 1},				// P1 Y
	{"FFFFFFFB", BTN_X, 1}				// P1 X
};

void findKeys(unsigned char *key, unsigned char *output) {
	unsigned char substr[8];

	memcpy(substr, &output[8], 8);
	substr[8]='\0';
	unsigned int value = ~strtoul(substr, NULL, 16);
	
	memset(key, 0, 32);

	if(debug) {
		printf("Output value: %s\n", output);
		printf("Hex value: 0x%08lX (0x%08lX)\n", value, ~value);
		printf("sizes: %d %d\n", sizeof(keys), sizeof(keys[0]));
	}

	for(int i=0 ; i < 32; i++) {
		if ((value & (1 <<i))) {
			key[i] =1;
			if(debug)
				printf("key[%02d]: %d\n", i, key[i]);
		}
	}
}

int setUInput(int player) {
	int fd;
    struct uinput_user_dev uidev;

	if(debug) {
		printf("Player: %d\n",player);
		printf("Condition: %s\n", (player == 1) ? "FUN R1 Player 1": "FUN R1 Player 2");
	}

	char *device_name = (player == 1) ? "FUN R1 Player 1": "FUN R1 Player 2";

    fd = open("/dev/uinput", O_WRONLY | O_NONBLOCK);
    if(fd < 0)
        die("error: open");

	ioctl(fd, UI_SET_EVBIT, EV_KEY);

	ioctl(fd, UI_SET_KEYBIT, BTN_TR);
	ioctl(fd, UI_SET_KEYBIT, BTN_TL);
	ioctl(fd, UI_SET_KEYBIT, BTN_A);
	ioctl(fd, UI_SET_KEYBIT, BTN_B);
	ioctl(fd, UI_SET_KEYBIT, BTN_X);
	ioctl(fd, UI_SET_KEYBIT, BTN_Y);
	ioctl(fd, UI_SET_KEYBIT, BTN_DPAD_LEFT);
	ioctl(fd, UI_SET_KEYBIT, BTN_DPAD_RIGHT);
	ioctl(fd, UI_SET_KEYBIT, BTN_DPAD_UP);
	ioctl(fd, UI_SET_KEYBIT, BTN_DPAD_DOWN);

	ioctl(fd, UI_SET_KEYBIT, BTN_START);
	ioctl(fd, UI_SET_KEYBIT, BTN_SELECT); // COIN/SELECT
	ioctl(fd, UI_SET_KEYBIT, BTN_BACK); // P1 BACK or P2 COIN/SELECT
	
	memset(&uidev, 0, sizeof(uidev));
	snprintf(uidev.name, UINPUT_MAX_NAME_SIZE, device_name);
	uidev.id.bustype = BUS_USB;
	uidev.id.vendor  = 0x1;
	uidev.id.product = 0x1;
	uidev.id.version = 1;

	if(write(fd, &uidev, sizeof(uidev)) < 0)
		die("error: write");

    if(ioctl(fd, UI_DEV_CREATE) < 0)
        die("error: ioctl");

	return fd;
}

int initUart(char * port) {
	int serial_port = open(port, O_RDWR | O_NOCTTY);

	struct termios tty;

	if(tcgetattr(serial_port, &tty) !=0) {
		printf("ERROR %i from tcgetattr: %s\n", errno, strerror(errno));
		return 1;
	}

	tty.c_cflag &= ~PARENB; // Clear parity bit, disabling parity (most common)
	tty.c_cflag &= ~CSTOPB; // Clear stop field, only one stop bit used in communication (most common)
	tty.c_cflag &= ~CSIZE; // Clear all bits that set the data size
	tty.c_cflag |= CS8; // 8 bits per byte (most common)
	tty.c_cflag &= ~CRTSCTS; // Disable RTS/CTS hardware flow control (most common)
	tty.c_cflag |= CREAD | CLOCAL; // Turn on READ & ignore ctrl lines (CLOCAL = 1)

	tty.c_lflag &= ~ICANON;
	tty.c_lflag &= ~ECHO; // Disable echo
	tty.c_lflag &= ~ECHOE; // Disable erasure
	tty.c_lflag &= ~ECHONL; // Disable new-line echo
	tty.c_lflag &= ~ISIG; // Disable interpretation of INTR, QUIT and SUSP
	tty.c_iflag &= ~(IXON | IXOFF | IXANY); // Turn off s/w flow ctrl
	tty.c_iflag &= ~(IGNBRK|BRKINT|PARMRK|ISTRIP|INLCR|IGNCR|ICRNL); // Disable any special handling of received bytes

	tty.c_oflag &= ~OPOST; // Prevent special interpretation of output bytes (e.g. newline chars)
	tty.c_oflag &= ~ONLCR; // Prevent conversion of newline to carriage return/line feed
	// tty.c_oflag &= ~OXTABS; // Prevent conversion of tabs to spaces (NOT PRESENT ON LINUX)
	// tty.c_oflag &= ~ONOEOT; // Prevent removal of C-d chars (0x004) in output (NOT PRESENT ON LINUX)

	//tty.c_cc[VTIME] = 200;    // Wait for up to 1s (10 deciseconds), returning as soon as any data is received.
	tty.c_cc[VMIN] = 9; // buffer size is 10

	// Set in/out baud rate to be 115200
	cfsetispeed(&tty, B115200);

	// Save tty settings, also checking for error
	if (tcsetattr(serial_port, TCSANOW, &tty) != 0) {
		printf("Error %i from tcsetattr: %s\n", errno, strerror(errno));
		return 1;
	}
	
	return serial_port;
}

int main(int argc, char *argv[]) {
    int                    p1_fd;
	int					   p2_fd;
    struct input_event     ev, ev1, ev2;
    int                    dx, dy;
    int                    i;
	char 				   *port;
	int 				   backIs2PCoin;

	if (argc == 4) {
		debug = atoi(argv[3]);
		port = argv[2];
		backIs2PCoin = atoi(argv[1]);
	} else if (argc == 3) {
		debug = 0;
		port = argv[2];
		backIs2PCoin = atoi(argv[1]);
	} else if (argc == 2) {
		debug = 0;
		port = "/dev/ttyAML2";
		backIs2PCoin = atoi(argv[1]);
	} else {
		debug = 0;
		port = "/dev/ttyAML2";
		backIs2PCoin = 1;
	}

	if(debug)
		printf("BACKIS2PCOIN: %d, PORT: %s, DEBUG: %d\n", backIs2PCoin, port, debug);


	p1_fd = setUInput(1);
	p2_fd = setUInput(2);

	int serial_port = initUart(port);

	unsigned char read_buf [10];

	unsigned char key[32] = {0};

	while(1) {
		memset(&read_buf, '\0', sizeof(read_buf));

		int num_bytes = read(serial_port, &read_buf, sizeof(read_buf));

		if (num_bytes < 0) {
			printf("Error reading: %s", strerror(errno));
			return 1;
		}

		if (num_bytes > 0) {
			unsigned char output[(10*2)+1];
			char *ptr = &output[0];
			for(int i = 0; i < 10 ; i++) {
				ptr += sprintf(ptr,"%0.2X", read_buf[i]);
			}

			findKeys(key, output);

			for(int i = 0; i < 32;i++) {
				if(debug)
					printf("key[%02d]: %d, key_code: %d\n", i, key[i], keys[i].key_code);

				memset(&ev, 0, sizeof(struct input_event));
				ev.type = EV_KEY;
				ev.code = keys[i].key_code;
				ev.value = key[i];

				if((keys[i].key_code == 278) && (backIs2PCoin == 2)) 
					keys[i].player = 2;

				if(write((keys[i].player == 1) ? p1_fd: p2_fd , &ev, sizeof(struct input_event)) < 0)
					die("error: write");
			}

			memset(&ev, 0, sizeof(struct input_event));
			ev.type = EV_SYN;
			ev.code = SYN_REPORT;
			ev.value = 0;
			if(write(p1_fd , &ev, sizeof(struct input_event)) < 0)
				die("error: write");	
			if(write(p2_fd , &ev, sizeof(struct input_event)) < 0)
				die("error: write");		
		}
	}

	if(ioctl(p1_fd, UI_DEV_DESTROY) < 0)
		die("error: ioctl");

	if(ioctl(p2_fd, UI_DEV_DESTROY) < 0)
		die("error: ioctl");

    close(p1_fd);
    close(p2_fd);
	close(serial_port);
	return 0; 
};

