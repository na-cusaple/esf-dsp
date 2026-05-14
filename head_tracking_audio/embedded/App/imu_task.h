#ifndef IMU_TASK_H
#define IMU_TASK_H

#include "stm32f4xx_hal.h"
#include "mpu6050.h"

HAL_StatusTypeDef imu_task_init(void);
void imu_task_update(void);
const mpu6050_raw_t *imu_task_get_latest(void);

#endif
