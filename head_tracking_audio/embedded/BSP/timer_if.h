#ifndef TIMER_IF_H
#define TIMER_IF_H

#include <stdbool.h>
#include "stm32f4xx_hal.h"

#ifndef TIMER_IF_HANDLE
#define TIMER_IF_HANDLE htim2
#endif

extern TIM_HandleTypeDef TIMER_IF_HANDLE;

HAL_StatusTypeDef timer_if_start(void);
HAL_StatusTypeDef timer_if_stop(void);
void timer_if_on_tick_isr(void);
bool timer_if_consume_tick(void);

#endif
