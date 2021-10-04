CC = gcc

MSG = -g -O0 -Wall
DEBUG = -D USE_DEBUG
STD = -std=gnu99
LIB = -lbcm2835 -lm -lrt -lpthread

OBJ_O = epaper.o config.o
# CFLAGS = -Wall -Werror -Wmissing-parameter-type -lblah 
CFLAGS = -std=c11 -Wall -Wextra -fPIC -Wmissing-parameter-type -lblah

bcmtest.so: bcmtest.c
	$(CC) ${CFLAGS} -c bcmtest.c -o bcmtest.o $(LIB)
	${CC} -fPIC -shared bcmtest.o -o bcmtest.so $(LIB)

epaper.so: ${OBJ_O}
	${CC} -fPIC -shared ${OBJ_O} -o epaper.so $(LIB)

epaper.o: EPD_IT8951.c EPD_IT8951.h
	$(CC) ${CFLAGS} -c EPD_IT8951.c -o epaper.o $(LIB)

config.o: DEV_Config.c DEV_Config.h
	$(CC) ${CFLAGS} -c DEV_Config.c -o config.o $(LIB)

clean:
	rm bcmtest.so
	rm epaper.so
	rm ./*.o
