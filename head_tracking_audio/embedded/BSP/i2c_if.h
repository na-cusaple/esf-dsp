#ifndef I2C_IF_H
#define I2C_IF_H

#include <stdint.h>
#include "stm32f4xx_hal.h"

#ifndef I2C_IF_TIMEOUT_MS
#define I2C_IF_TIMEOUT_MS 100
#endif

#ifndef I2C_IF_HANDLE
#define I2C_IF_HANDLE hi2c1
#endif

extern I2C_HandleTypeDef I2C_IF_HANDLE;

HAL_StatusTypeDef i2c_if_write_reg(uint8_t dev_addr, uint8_t reg, uint8_t value);
HAL_StatusTypeDef i2c_if_read_reg(uint8_t dev_addr, uint8_t reg, uint8_t *value);
HAL_StatusTypeDef i2c_if_read_regs(uint8_t dev_addr, uint8_t reg, uint8_t *buf, uint16_t len);

#endif
