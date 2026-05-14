#include "uart_if.h"
#include <string.h>

static volatile bool uart_tx_busy = false;

HAL_StatusTypeDef uart_if_init(void)
{
    return HAL_OK;
}

bool uart_if_is_tx_busy(void)
{
    return uart_tx_busy;
}

HAL_StatusTypeDef uart_if_tx_dma(const uint8_t *data, uint16_t len)
{
    HAL_StatusTypeDef status;

    if (data == NULL || len == 0)
    {
        return HAL_ERROR;
    }
    if (uart_tx_busy)
    {
        return HAL_BUSY;
    }

    uart_tx_busy = true;
    status = HAL_UART_Transmit_DMA(&UART_IF_HANDLE, (uint8_t *)data, len);
    if (status != HAL_OK)
    {
        uart_tx_busy = false;
    }
    return status;
}

HAL_StatusTypeDef uart_if_tx_blocking(const uint8_t *data, uint16_t len, uint32_t timeout_ms)
{
    if (data == NULL || len == 0)
    {
        return HAL_ERROR;
    }
    return HAL_UART_Transmit(&UART_IF_HANDLE, (uint8_t *)data, len, timeout_ms);
}

HAL_StatusTypeDef uart_if_write_debug(const char *str)
{
    if (str == NULL)
    {
        return HAL_ERROR;
    }
    return uart_if_tx_blocking((const uint8_t *)str, (uint16_t)strlen(str), UART_IF_TIMEOUT_MS);
}

void uart_if_on_tx_complete(void)
{
    uart_tx_busy = false;
}
