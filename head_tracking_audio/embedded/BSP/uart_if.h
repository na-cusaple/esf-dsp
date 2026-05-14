#ifndef UART_IF_H
#define UART_IF_H

#include <stdbool.h>
#include <stdint.h>
#include "stm32f4xx_hal.h"

#ifndef UART_IF_HANDLE
#define UART_IF_HANDLE huart2
#endif

#ifndef UART_IF_TIMEOUT_MS
#define UART_IF_TIMEOUT_MS 100
#endif

extern UART_HandleTypeDef UART_IF_HANDLE;

HAL_StatusTypeDef uart_if_init(void);
HAL_StatusTypeDef uart_if_tx_dma(const uint8_t *data, uint16_t len);
HAL_StatusTypeDef uart_if_tx_blocking(const uint8_t *data, uint16_t len, uint32_t timeout_ms);
HAL_StatusTypeDef uart_if_write_debug(const char *str);
void uart_if_on_tx_complete(void);
bool uart_if_is_tx_busy(void);

#endif
