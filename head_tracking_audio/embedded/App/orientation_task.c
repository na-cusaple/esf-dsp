#include "orientation_task.h"

#define GYRO_SENS_500DPS 65.5f
#define ACCEL_SENS_4G 8192.0f
#define MADGWICK_BETA 0.05f
#define DEG_TO_RAD 0.0174532925f

static float gyro_bias_x = 0.0f;
static float gyro_bias_y = 0.0f;
static float gyro_bias_z = 0.0f;
static Quaternion_t orientation_q;

HAL_StatusTypeDef orientation_task_init(uint16_t gyro_calib_samples)
{
    uint32_t i;
    int64_t sum_gx = 0;
    int64_t sum_gy = 0;
    int64_t sum_gz = 0;
    mpu6050_raw_t raw;

    Madgwick_Init(MADGWICK_BETA);
    if (gyro_calib_samples == 0)
    {
        return HAL_ERROR;
    }

    for (i = 0; i < gyro_calib_samples; ++i)
    {
        if (MPU6050_ReadRaw(&raw) != HAL_OK)
        {
            return HAL_ERROR;
        }
        sum_gx += raw.gx;
        sum_gy += raw.gy;
        sum_gz += raw.gz;
        HAL_Delay(2);
    }

    gyro_bias_x = (float)sum_gx / (float)gyro_calib_samples;
    gyro_bias_y = (float)sum_gy / (float)gyro_calib_samples;
    gyro_bias_z = (float)sum_gz / (float)gyro_calib_samples;
    orientation_q = Madgwick_GetQuaternion();
    return HAL_OK;
}

void orientation_task_update(const mpu6050_raw_t *raw, float dt)
{
    float ax_g;
    float ay_g;
    float az_g;
    float gx_dps;
    float gy_dps;
    float gz_dps;
    float gx_rad;
    float gy_rad;
    float gz_rad;

    if (raw == NULL)
    {
        return;
    }

    ax_g = (float)raw->ax / ACCEL_SENS_4G;
    ay_g = (float)raw->ay / ACCEL_SENS_4G;
    az_g = (float)raw->az / ACCEL_SENS_4G;

    gx_dps = ((float)raw->gx - gyro_bias_x) / GYRO_SENS_500DPS;
    gy_dps = ((float)raw->gy - gyro_bias_y) / GYRO_SENS_500DPS;
    gz_dps = ((float)raw->gz - gyro_bias_z) / GYRO_SENS_500DPS;

    gx_rad = gx_dps * DEG_TO_RAD;
    gy_rad = gy_dps * DEG_TO_RAD;
    gz_rad = gz_dps * DEG_TO_RAD;

    Madgwick_UpdateIMU(gx_rad, gy_rad, gz_rad, ax_g, ay_g, az_g, dt);
    orientation_q = Madgwick_GetQuaternion();
}

const Quaternion_t *orientation_task_get_quaternion(void)
{
    return &orientation_q;
}
