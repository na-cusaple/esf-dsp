#include "i2c_if.h"

static uint16_t i2c_if_addr_8bit(uint8_t addr7)
{
    return (uint16_t)(addr7 << 1);
}

HAL_StatusTypeDef i2c_if_write_reg(uint8_t dev_addr, uint8_t reg, uint8_t value)
{
    return HAL_I2C_Mem_Write(
        &I2C_IF_HANDLE,
        i2c_if_addr_8bit(dev_addr),
        reg,
        I2C_MEMADD_SIZE_8BIT,
        &value,
        1,
        I2C_IF_TIMEOUT_MS);
}

HAL_StatusTypeDef i2c_if_read_reg(uint8_t dev_addr, uint8_t reg, uint8_t *value)
{
    if (value == NULL)
    {
        return HAL_ERROR;
    }
    return HAL_I2C_Mem_Read(
        &I2C_IF_HANDLE,
        i2c_if_addr_8bit(dev_addr),
        reg,
        I2C_MEMADD_SIZE_8BIT,
        value,
        1,
        I2C_IF_TIMEOUT_MS);
}

HAL_StatusTypeDef i2c_if_read_regs(uint8_t dev_addr, uint8_t reg, uint8_t *buf, uint16_t len)
{
    if (buf == NULL || len == 0)
    {
        return HAL_ERROR;
    }
    return HAL_I2C_Mem_Read(
        &I2C_IF_HANDLE,
        i2c_if_addr_8bit(dev_addr),
        reg,
        I2C_MEMADD_SIZE_8BIT,
        buf,
        len,
        I2C_IF_TIMEOUT_MS);
}
