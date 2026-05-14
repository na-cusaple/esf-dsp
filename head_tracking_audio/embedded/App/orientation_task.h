#ifndef ORIENTATION_TASK_H
#define ORIENTATION_TASK_H

#include <stdint.h>
#include "stm32f4xx_hal.h"

#include "madgwick.h"
#include "mpu6050.h"

HAL_StatusTypeDef orientation_task_init(uint16_t gyro_calib_samples);
void orientation_task_update(const mpu6050_raw_t *raw, float dt);
const Quaternion_t *orientation_task_get_quaternion(void);

#endif
