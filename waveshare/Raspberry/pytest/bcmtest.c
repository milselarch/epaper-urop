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
	int start_x, int start_y,
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
			EPD_IT8951_1bp_Multi_Frame_Write(
				REFRESH_FRAME_BUF, start_x, start_y,
				panel_width, panel_height, mem_addr, false
			);
			EPD_IT8951_1bp_Multi_Frame_Refresh(
				start_x, start_y, panel_width, 
				panel_height, mem_addr
			);
			/*
			EPD_IT8951_1bp_Refresh(
				REFRESH_FRAME_BUF, start_x, start_y,
				width, height, A2_Mode, mem_addr, false
			);
			*/
			break;
		} case 2: {
			EPD_IT8951_2bp_Refresh(
				REFRESH_FRAME_BUF, start_x, start_y,
				panel_width,  panel_height, A2_Mode, mem_addr, false
			);
			break;
		} case 4: {
			EPD_IT8951_4bp_Refresh(
				REFRESH_FRAME_BUF, start_x, start_y,
				panel_width,  panel_height, A2_Mode, mem_addr, false
			);
			break;
		} case 8: {
			EPD_IT8951_8bp_Refresh(
				REFRESH_FRAME_BUF, start_x, start_y,
				panel_width, panel_height, A2_Mode, mem_addr
			);
			break;
		}
	}
}

void fast_refresh(
	UBYTE* Frame_Buf, UWORD X, UWORD Y, UWORD W, UWORD H, 
	bool Hold, UDOUBLE Target_Memory_Addr, bool Packed_Write
) {
    IT8951_Load_Img_Info Load_Img_Info;
    IT8951_Area_Img_Info Area_Img_Info;

    // EPD_IT8951_WaitForDisplayReady();

    Load_Img_Info.Source_Buffer_Addr = (UDOUBLE) Frame_Buf;
    Load_Img_Info.Endian_Type = IT8951_LDIMG_L_ENDIAN;
    Load_Img_Info.Pixel_Format = IT8951_2BPP;
    Load_Img_Info.Rotate =  IT8951_ROTATE_0;
    Load_Img_Info.Target_Memory_Addr = Target_Memory_Addr;

    Area_Img_Info.Area_X = X;
    Area_Img_Info.Area_Y = Y;
    Area_Img_Info.Area_W = W;
    Area_Img_Info.Area_H = H;

    EPD_IT8951_HostAreaPackedPixelWrite_2bp(
        &Load_Img_Info, &Area_Img_Info, Packed_Write
    );

	EPD_IT8951_Display_AreaBuf(X,Y,W,H, GC16_Mode,Target_Memory_Addr);

	/*
    if (Hold == true) {
        EPD_IT8951_Display_Area(X,Y,W,H, GC16_Mode);
	} else {
        EPD_IT8951_Display_AreaBuf(X,Y,W,H, GC16_Mode,Target_Memory_Addr);
    }
	*/
}

void multi_frame_write(
	UBYTE* Frame_Buf, UWORD X, UWORD Y, UWORD W, UWORD H,
	UDOUBLE Target_Memory_Addr, bool Packed_Write
) {
    IT8951_Load_Img_Info Load_Img_Info;
    IT8951_Area_Img_Info Area_Img_Info;

    EPD_IT8951_WaitForDisplayReady();

    Load_Img_Info.Source_Buffer_Addr = (UDOUBLE)Frame_Buf;
    Load_Img_Info.Endian_Type = IT8951_LDIMG_L_ENDIAN;
    //Use 8bpp to set 1bpp
    Load_Img_Info.Pixel_Format = IT8951_8BPP;
    Load_Img_Info.Rotate = IT8951_ROTATE_0;
    Load_Img_Info.Target_Memory_Addr = Target_Memory_Addr;

    Area_Img_Info.Area_X = X/8;
    Area_Img_Info.Area_Y = Y;
    Area_Img_Info.Area_W = W/8;
    Area_Img_Info.Area_H = H;

    EPD_IT8951_HostAreaPackedPixelWrite_1bp(
		&Load_Img_Info, &Area_Img_Info, Packed_Write
	);
	EPD_IT8951_1bp_Multi_Frame_Refresh(
		X, Y, W, H, Target_Memory_Addr
	);
}

int fast_draw_grayscale_array(
	UWORD start_x, UWORD start_y,
	UWORD width, UWORD height, const UBYTE *arr
) {
	if (!INITIALISED) {
		return -1;
	} if (REFRESH_FRAME_BUF == NULL) {
		// return 0;
	}

	UDOUBLE mem_addr = get_mem_addr(DEV_INFO);
	int panel_width = DEV_INFO.Panel_W;
    int panel_height = DEV_INFO.Panel_H;

	const int bits_per_pixel = 1;
	const long image_size = (
		(width * 1 % 8 == 0) ? (width * 1 / 8 ):
		(width * 1 / 8 + 1)
	) * height;

	REFRESH_FRAME_BUF = (UBYTE *) malloc (image_size);

	UWORD x, y;
	UBYTE gray;
	printf("INIT MATRIX RENDER \r\n");
	
	Paint_NewImage(REFRESH_FRAME_BUF, width, height, 0, WHITE);
	Paint_SelectImage(REFRESH_FRAME_BUF);
	Epd_Mode(epd_mode);
	Paint_SetBitsPerPixel(1);

	for (y=0; y<height; y++) {
		for (x=0; x<width; x++) {
			// gray = (R*299 + G*587 + B*114 + 500) / 1000;
			gray = arr[y * width + x];
			Paint_SetPixel(x, y, gray);
		}
	}

	printf("[%d,%d]: %d\n", x, y, gray);
	printf("DONE MATRIX RENDER \r\n");
	printf("epd_mode: %d \r\n", epd_mode);
	// referenced from main.c
	//10.3inch e-Paper HAT(1872,1404)

	EPD_IT8951_1bp_Multi_Frame_Write(
		REFRESH_FRAME_BUF, start_x, start_y, width,
		height, mem_addr, false
	);

	EPD_IT8951_1bp_Multi_Frame_Refresh(
		start_x, start_y, width, height, 
		mem_addr
	);

	if (REFRESH_FRAME_BUF != NULL) {
        free(REFRESH_FRAME_BUF);
        REFRESH_FRAME_BUF = NULL;
    }

	/*
	multi_frame_write(
		REFRESH_FRAME_BUF, start_x, start_y, 
		width, height, mem_addr, false
	);
	EPD_IT8951_1bp_Multi_Frame_Write(
		REFRESH_FRAME_BUF, start_x, start_y,
		width, height, mem_addr, false
	);
	EPD_IT8951_1bp_Multi_Frame_Refresh(
		start_x, start_y, width, height, mem_addr
	);
	*/
}

int Dynamic_GIF_Example(
) {
	UDOUBLE mem_addr = get_mem_addr(DEV_INFO);
	int panel_width = DEV_INFO.Panel_W;
    int panel_height = DEV_INFO.Panel_H;

    UWORD Animation_Start_X = 0;
    UWORD Animation_Start_Y = 0;
    UWORD Animation_Area_Width = 800;
    UWORD Animation_Area_Height = 600;

    if (Animation_Area_Width > panel_width) {
        return -1;
    }
    if (Animation_Area_Height > panel_height) {
        return -1;
    }

    UDOUBLE Imagesize;

    UBYTE Pic_Count = 0;
    UBYTE Pic_Num = 7;
    // char Path[30];

    UDOUBLE Basical_Memory_Addr = mem_addr;

    UDOUBLE Target_Memory_Addr = Basical_Memory_Addr;
    UWORD Repeat_Animation_Times = 0;

    clock_t Animation_Test_Start, Animation_Test_Finish;
    double Animation_Test_Duration;

    Imagesize = ((Animation_Area_Width * 1 % 8 == 0)? (Animation_Area_Width * 1 / 8 ): (Animation_Area_Width * 1 / 8 + 1)) * Animation_Area_Height;

    if ((REFRESH_FRAME_BUF = (UBYTE *) malloc(Imagesize)) == NULL) {
        Debug("Failed to apply for image memory...\r\n");
        return -1;
    }

    Paint_NewImage(REFRESH_FRAME_BUF, Animation_Area_Width, Animation_Area_Height, 0, BLACK);
    Paint_SelectImage(REFRESH_FRAME_BUF);
	Epd_Mode(epd_mode);
    Paint_SetBitsPerPixel(1);

	Paint_Clear(WHITE);

	char path[30] = "./pic/800x600_0.bmp";
	GUI_ReadBmp(path, 0, 0);

	if(epd_mode == 2) {
		EPD_IT8951_1bp_Multi_Frame_Write(REFRESH_FRAME_BUF, 1280-Animation_Area_Width+Animation_Start_X, Animation_Start_Y, Animation_Area_Width,  Animation_Area_Height, Target_Memory_Addr,false);
	} else if (epd_mode == 1) {
		EPD_IT8951_1bp_Multi_Frame_Write(REFRESH_FRAME_BUF, panel_width-Animation_Area_Width+Animation_Start_X-16, Animation_Start_Y, Animation_Area_Width,  Animation_Area_Height, Target_Memory_Addr,false);
	} else {
		EPD_IT8951_1bp_Multi_Frame_Write(REFRESH_FRAME_BUF, Animation_Start_X, Animation_Start_Y, Animation_Area_Width,  Animation_Area_Height, Target_Memory_Addr,false);
	}

    Animation_Test_Finish = clock();
    Animation_Test_Duration = (double)(Animation_Test_Finish - Animation_Test_Start) / CLOCKS_PER_SEC;
	Debug( "Write all frame occupy %f second\r\n", Animation_Test_Duration);
    Debug(" Write FPS: %f \r\n", Pic_Num / Animation_Test_Duration);

    Target_Memory_Addr = Basical_Memory_Addr;

	if (epd_mode == 2) {
		EPD_IT8951_1bp_Multi_Frame_Refresh(panel_width-Animation_Area_Width+Animation_Start_X, Animation_Start_Y, Animation_Area_Width,  Animation_Area_Height, Target_Memory_Addr);
	} else if(epd_mode == 1) {
		EPD_IT8951_1bp_Multi_Frame_Refresh(panel_width-Animation_Area_Width+Animation_Start_X-16, Animation_Start_Y, Animation_Area_Width,  Animation_Area_Height, Target_Memory_Addr);
	} else {
		EPD_IT8951_1bp_Multi_Frame_Refresh(Animation_Start_X, Animation_Start_Y, Animation_Area_Width,  Animation_Area_Height, Target_Memory_Addr);
	}
	
    if (REFRESH_FRAME_BUF != NULL) {
        free(REFRESH_FRAME_BUF);
        REFRESH_FRAME_BUF = NULL;
    }

    return 0;
}