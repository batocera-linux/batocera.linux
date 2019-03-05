#EXECS = retrogame gamera
EXECS = retrogame 
CC    = gcc $(CFLAGS) -Wall -O3 -fomit-frame-pointer -funroll-loops -s

all: $(EXECS)

retrogame: retrogame.c
	$(CC) $< -o $@

gamera: gamera.c
	$(CC) $< -lncurses -lmenu -lexpat -o $@

install:
	mv $(EXECS) /usr/local/bin

clean:
	rm -f $(EXECS)
