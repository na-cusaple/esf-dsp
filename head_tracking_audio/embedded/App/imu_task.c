#include "imu_task.h"
#include "orientation_task.h"
#include "stream_task.h"
#include "timer_if.h"

static mpu6050_raw_t imu_raw;
static const float imu_dt_sec = 0.005f;

HAL_StatusTypeDef imu_task_init(void)
{
    HAL_StatusTypeDef status = MPU6050_Init();
    if (status != HAL_OK)
    {
        return status;
    }

    return orientation_task_init(500);
}

const mpu6050_raw_t *imu_task_get_latest(void)
{
    return &imu_raw;
}

void imu_task_update(void)
{
    if (!timer_if_consume_tick())
    {
        return;
    }

    if (MPU6050_ReadRaw(&imu_raw) != HAL_OK)
    {
        return;
    }

    orientation_task_update(&imu_raw, imu_dt_sec);
    stream_task_send_quaternion(orientation_task_get_quaternion());
}
