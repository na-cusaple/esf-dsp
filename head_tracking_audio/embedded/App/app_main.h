#ifndef APP_MAIN_H
#define APP_MAIN_H

#include "stm32f4xx_hal.h"

HAL_StatusTypeDef app_main_init(void);
void app_main_loop(void);
void app_main_on_timer_tick(void);
void app_main_on_uart_tx_complete(UART_HandleTypeDef *huart);

#endif
