#ifndef MPU6050_H
#define MPU6050_H

#include <stdbool.h>
#include <stdint.h>
#include "stm32f4xx_hal.h"

#define MPU6050_ADDR 0x68

/* Register map */
#define MPU6050_REG_SMPLRT_DIV 0x19
#define MPU6050_REG_CONFIG 0x1A
#define MPU6050_REG_GYRO_CONFIG 0x1B
#define MPU6050_REG_ACCEL_CONFIG 0x1C
#define MPU6050_REG_ACCEL_XOUT_H 0x3B
#define MPU6050_REG_TEMP_OUT_H 0x41
#define MPU6050_REG_GYRO_XOUT_H 0x43
#define MPU6050_REG_PWR_MGMT_1 0x6B
#define MPU6050_REG_WHO_AM_I 0x75

#define MPU6050_WHO_AM_I_VALUE 0x68

typedef enum
{
    MPU6050_GYRO_250DPS = 0,
    MPU6050_GYRO_500DPS = 1,
    MPU6050_GYRO_1000DPS = 2,
    MPU6050_GYRO_2000DPS = 3,
} mpu6050_gyro_range_t;

typedef enum
{
    MPU6050_ACCEL_2G = 0,
    MPU6050_ACCEL_4G = 1,
    MPU6050_ACCEL_8G = 2,
    MPU6050_ACCEL_16G = 3,
} mpu6050_accel_range_t;

typedef enum
{
    MPU6050_DLPF_260HZ = 0,
    MPU6050_DLPF_184HZ = 1,
    MPU6050_DLPF_94HZ = 2,
    MPU6050_DLPF_42HZ = 3,
    MPU6050_DLPF_20HZ = 4,
    MPU6050_DLPF_10HZ = 5,
    MPU6050_DLPF_5HZ = 6,
} mpu6050_dlpf_t;

typedef struct
{
    int16_t ax;
    int16_t ay;
    int16_t az;
    int16_t gx;
    int16_t gy;
    int16_t gz;
} mpu6050_raw_t;

HAL_StatusTypeDef MPU6050_Init(void);
HAL_StatusTypeDef MPU6050_TestConnection(void);
HAL_StatusTypeDef MPU6050_ReadRaw(mpu6050_raw_t *raw);
HAL_StatusTypeDef MPU6050_ReadAccel(int16_t *ax, int16_t *ay, int16_t *az);
HAL_StatusTypeDef MPU6050_ReadGyro(int16_t *gx, int16_t *gy, int16_t *gz);

#endif
