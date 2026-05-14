#ifndef STREAM_TASK_H
#define STREAM_TASK_H

#include "stm32f4xx_hal.h"
#include "quaternion.h"

HAL_StatusTypeDef stream_task_send_quaternion(const Quaternion_t *q);

#endif
