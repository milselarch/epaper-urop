// #include "GUI_Paint.c"
#include "../e-Paper/EPD_IT8951.h"
#include "GUI_Paint.h"
#include "../Config/Debug.h"

#include <fcntl.h>
#include <unistd.h>
#include <stdint.h>
#include <stdlib.h>  // exit()
#include <string.h>  // memset()
#include <math.h>    // memset()
#include <stdio.h>

bool screen_initialised = false;
UBYTE has_color;

void set_epd_mode(int mode) {
	if (mode == 3) {
		Paint_SetRotate(ROTATE_0);
		Paint_SetMirroring(MIRROR_NONE);
		has_color = 1;
	} else if (mode == 2) {
		Paint_SetRotate(ROTATE_0);
		Paint_SetMirroring(MIRROR_HORIZONTAL);
	} else if (mode == 1) {
		Paint_SetRotate(ROTATE_0);
		Paint_SetMirroring(MIRROR_HORIZONTAL);
	} else {
		Paint_SetRotate(ROTATE_0);
		Paint_SetMirroring(MIRROR_NONE);
	}
}

int test(int VCOM) {
	printf("TESTING");
	return 2;
}

int init_screen(int VCOM) {
	UBYTE bits_per_pixel = 8;
	int epd_mode = 0;
	
	EPD_IT8951_Init(VCOM);
	// EPD_IT8951_Reset();

    // EPD_IT8951_SystemRun();
	
	//IT8951_Dev_Info dev_info = EPD_IT8951_Init(VCOM);
	/*
	screen_initialised = true;

	UWORD width = dev_info.Panel_W;
	UWORD height = dev_info.Panel_H;

	UDOUBLE image_size = (
		(width * bits_per_pixel % 8 == 0) ? 
		(width * bits_per_pixel / 8 ):
		(width * bits_per_pixel / 8 + 1)
	) * height;
	
	UBYTE *refresh_buffer = NULL;
	refresh_buffer = (UBYTE *) malloc (image_size);

	if (refresh_buffer == NULL) {
		Debug("Failed to apply for black memory...\r\n");
		return -1;
	}

	Paint_NewImage(refresh_buffer, width, height, 0, BLACK);
	Paint_SelectImage(refresh_buffer);
	set_epd_mode(epd_mode);
	Paint_SetBitsPerPixel(bits_per_pixel);
	Paint_Clear(WHITE);
	*/
	return 1;
}

void draw_grayscale_array(
	UWORD width, UWORD height, const UBYTE *arr
) {
	UWORD i, j, x, y;
	UBYTE R, G, B;
	UBYTE temp1, temp2;
	UBYTE gray;
	
	for (y=0; y<height; y++) {
		for (x=0; x<width; x++) {
			// gray = (R*299 + G*587 + B*114 + 500) / 1000;
			gray = arr[y * height + x];     
			Paint_SetPixel(i, j, gray);
		}

		printf("[%d,%d]: %d\n", x, y, gray);
	}
}