#include "mpu6050.h"
#include "i2c_if.h"

#define MPU6050_SMPLRT_DIV_200HZ 4
#define MPU6050_GYRO_RANGE MPU6050_GYRO_500DPS
#define MPU6050_ACCEL_RANGE MPU6050_ACCEL_4G
#define MPU6050_DLPF_CFG MPU6050_DLPF_42HZ

static HAL_StatusTypeDef mpu6050_write_reg(uint8_t reg, uint8_t value)
{
    return i2c_if_write_reg(MPU6050_ADDR, reg, value);
}

static HAL_StatusTypeDef mpu6050_read_reg(uint8_t reg, uint8_t *value)
{
    return i2c_if_read_reg(MPU6050_ADDR, reg, value);
}

static HAL_StatusTypeDef mpu6050_read_regs(uint8_t reg, uint8_t *buf, uint16_t len)
{
    return i2c_if_read_regs(MPU6050_ADDR, reg, buf, len);
}

static HAL_StatusTypeDef mpu6050_read_who_am_i(uint8_t *who)
{
    if (who == NULL)
    {
        return HAL_ERROR;
    }
    return mpu6050_read_reg(MPU6050_REG_WHO_AM_I, who);
}

HAL_StatusTypeDef MPU6050_TestConnection(void)
{
    uint8_t who = 0;
    HAL_StatusTypeDef status = mpu6050_read_who_am_i(&who);
    if (status != HAL_OK)
    {
        return status;
    }
    return (who == MPU6050_WHO_AM_I_VALUE) ? HAL_OK : HAL_ERROR;
}

HAL_StatusTypeDef MPU6050_Init(void)
{
    HAL_StatusTypeDef status = MPU6050_TestConnection();
    if (status != HAL_OK)
    {
        return status;
    }

    status = mpu6050_write_reg(MPU6050_REG_PWR_MGMT_1, 0x00);
    if (status != HAL_OK)
    {
        return status;
    }

    status = mpu6050_write_reg(MPU6050_REG_SMPLRT_DIV, MPU6050_SMPLRT_DIV_200HZ);
    if (status != HAL_OK)
    {
        return status;
    }

    status = mpu6050_write_reg(MPU6050_REG_CONFIG, (uint8_t)MPU6050_DLPF_CFG);
    if (status != HAL_OK)
    {
        return status;
    }

    status = mpu6050_write_reg(MPU6050_REG_GYRO_CONFIG, (uint8_t)(MPU6050_GYRO_RANGE << 3));
    if (status != HAL_OK)
    {
        return status;
    }

    status = mpu6050_write_reg(MPU6050_REG_ACCEL_CONFIG, (uint8_t)(MPU6050_ACCEL_RANGE << 3));
    return status;
}

HAL_StatusTypeDef MPU6050_ReadRaw(mpu6050_raw_t *raw)
{
    uint8_t buf[14];
    if (raw == NULL)
    {
        return HAL_ERROR;
    }

    if (mpu6050_read_regs(MPU6050_REG_ACCEL_XOUT_H, buf, sizeof(buf)) != HAL_OK)
    {
        return HAL_ERROR;
    }

    raw->ax = (int16_t)((buf[0] << 8) | buf[1]);
    raw->ay = (int16_t)((buf[2] << 8) | buf[3]);
    raw->az = (int16_t)((buf[4] << 8) | buf[5]);

    raw->gx = (int16_t)((buf[8] << 8) | buf[9]);
    raw->gy = (int16_t)((buf[10] << 8) | buf[11]);
    raw->gz = (int16_t)((buf[12] << 8) | buf[13]);
    return HAL_OK;
}

HAL_StatusTypeDef MPU6050_ReadAccel(int16_t *ax, int16_t *ay, int16_t *az)
{
    mpu6050_raw_t raw;
    HAL_StatusTypeDef status = MPU6050_ReadRaw(&raw);
    if (status != HAL_OK)
    {
        return status;
    }
    if (ax)
    {
        *ax = raw.ax;
    }
    if (ay)
    {
        *ay = raw.ay;
    }
    if (az)
    {
        *az = raw.az;
    }
    return HAL_OK;
}

HAL_StatusTypeDef MPU6050_ReadGyro(int16_t *gx, int16_t *gy, int16_t *gz)
{
    mpu6050_raw_t raw;
    HAL_StatusTypeDef status = MPU6050_ReadRaw(&raw);
    if (status != HAL_OK)
    {
        return status;
    }
    if (gx)
    {
        *gx = raw.gx;
    }
    if (gy)
    {
        *gy = raw.gy;
    }
    if (gz)
    {
        *gz = raw.gz;
    }
    return HAL_OK;
}
