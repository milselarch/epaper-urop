#include <bcm2835.h>
#include "EPD_IT8951.h"
#include "EPD_IT8951.c"
#include "DEV_Config.c"
#include "GUI_Paint.c"
#include "GUI_BMPfile.c"
#include "fonts.h"
#include "Debug.h"
#include <stdio.h>

// const int EPD_RST_PIN = 17;
const int high = 1;
const UWORD VCOM = 1520;

// bool Four_Byte_Align = false;
UBYTE *REFRESH_FRAME_BUF = NULL;
IT8951_Dev_Info DEV_INFO;
bool INITIALISED = false;

unsigned int epd_mode = 2;


UDOUBLE get_mem_addr(IT8951_Dev_Info dev_info) {
	UDOUBLE mem_addr = (
		dev_info.Memory_Addr_L | (dev_info.Memory_Addr_H << 16)
	);
	return mem_addr;
}

int reset() {
	int status = DEV_Module_Init();
	if (status == 1) {
		return -1;
	}

	DEV_GPIO_Init();

	DEV_INFO = EPD_IT8951_Init(VCOM);
	int panel_width = DEV_INFO.Panel_W;
    int panel_height = DEV_INFO.Panel_H;
	printf("dimensions: %d x %d \r\n", panel_width, panel_height);

	UDOUBLE mem_addr = get_mem_addr(DEV_INFO);
	EPD_IT8951_Clear_Refresh(DEV_INFO, mem_addr, INIT_Mode);
	INITIALISED = true;
    return 1;
}

static void Epd_Mode(int mode) {
	if (mode == 3) {
		Paint_SetRotate(ROTATE_0);
		Paint_SetMirroring(MIRROR_NONE);
		isColor = 1;
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

void clear_screen(UBYTE bits_per_pixel) {
	UDOUBLE mem_addr = get_mem_addr(DEV_INFO);
	EPD_IT8951_Clear_Refresh(DEV_INFO, mem_addr, GC16_Mode);

	int panel_width = DEV_INFO.Panel_W;
    int panel_height = DEV_INFO.Panel_H;

	/*
	Display_ColorPalette_Example(
		panel_width, panel_height, mem_addr
	);
	EPD_IT8951_Clear_Refresh(dev_info, mem_addr, GC16_Mode);
	Display_BMP_Example(
		panel_width, panel_height, mem_addr, 4
	);
	*/

	printf("PAINT START \r\n");
	
	UDOUBLE Imagesize;

	Imagesize = (
		(panel_width * bits_per_pixel % 8 == 0) ?
		 (panel_width * bits_per_pixel / 8 ): 
		 (panel_width * bits_per_pixel / 8 + 1)
	) * panel_height;

	REFRESH_FRAME_BUF = (UBYTE *) malloc (Imagesize);

	Paint_NewImage(
		REFRESH_FRAME_BUF, panel_width, panel_height, 0, BLACK
	);

    Paint_SelectImage(REFRESH_FRAME_BUF);
	Epd_Mode(epd_mode);
    Paint_SetBitsPerPixel(bits_per_pixel);
    Paint_Clear(WHITE);

	EPD_IT8951_Clear_Refresh(DEV_INFO, mem_addr, GC16_Mode);
}

void change_bits_per_pixel(UBYTE bits_per_pixel) {
	UDOUBLE mem_addr = get_mem_addr(DEV_INFO);

	int panel_width = DEV_INFO.Panel_W;
    int panel_height = DEV_INFO.Panel_H;

	/*
	Display_ColorPalette_Example(
		panel_width, panel_height, mem_addr
	);
	EPD_IT8951_Clear_Refresh(dev_info, mem_addr, GC16_Mode);
	Display_BMP_Example(
		panel_width, panel_height, mem_addr, 4
	);
	*/

	printf("PAINT START \r\n");
	
	UDOUBLE Imagesize;

	Imagesize = (
		(panel_width * bits_per_pixel % 8 == 0) ?
		 (panel_width * bits_per_pixel / 8 ): 
		 (panel_width * bits_per_pixel / 8 + 1)
	) * panel_height;

	REFRESH_FRAME_BUF = (UBYTE *) malloc (Imagesize);

	Paint_NewImage(
		REFRESH_FRAME_BUF, panel_width, panel_height, 0, BLACK
	);

    Paint_SelectImage(REFRESH_FRAME_BUF);
	Epd_Mode(epd_mode);
	Paint_SetBitsPerPixel(bits_per_pixel);
}

int draw_grayscale_array(
	UWORD width, UWORD height, UBYTE bits_per_pixel,
	const UBYTE *arr
) {
	if (!INITIALISED) {
		return -1;
	} if (REFRESH_FRAME_BUF == NULL) {
		return 0;
	}

	UDOUBLE mem_addr = get_mem_addr(DEV_INFO);
	int panel_width = DEV_INFO.Panel_W;
    int panel_height = DEV_INFO.Panel_H;

	UWORD x, y;
	UBYTE gray;
	printf("INIT MATRIX RENDER \r\n");
	
	for (y=0; y<height; y++) {
		for (x=0; x<width; x++) {
			// gray = (R*299 + G*587 + B*114 + 500) / 1000;
			gray = arr[y * width + x];
			Paint_SetPixel(x, y, gray);
		}
	}

	printf("[%d,%d]: %d\n", x, y, gray);
	printf("DONE MATRIX RENDER \r\n");
	// referenced from main.c
	//10.3inch e-Paper HAT(1872,1404)
	A2_Mode = 6;

	switch (bits_per_pixel) {
		case 1: {
			EPD_IT8951_1bp_Refresh(
				REFRESH_FRAME_BUF, 0, 0, panel_width,  panel_height,
				A2_Mode, mem_addr, false
			);
			break;
		} case 2: {
			EPD_IT8951_2bp_Refresh(
				REFRESH_FRAME_BUF, 0, 0, panel_width,  panel_height,
				A2_Mode, mem_addr, false
			);
			break;
		} case 4: {
			EPD_IT8951_4bp_Refresh(
				REFRESH_FRAME_BUF, 0, 0, panel_width,  panel_height,
				A2_Mode, mem_addr, false
			);
			break;
		} case 8: {
			EPD_IT8951_8bp_Refresh(
				REFRESH_FRAME_BUF, 0, 0, panel_width,  panel_height,
				A2_Mode, mem_addr
			);
			break;
		}
	}
}