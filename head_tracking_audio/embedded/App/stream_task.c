#include "stream_task.h"
#include "uart_if.h"
#include <stdio.h>

HAL_StatusTypeDef stream_task_send_quaternion(const Quaternion_t *q)
{
    char line[96];
    int len;
    uint32_t timestamp_ms;

    if (q == NULL)
    {
        return HAL_ERROR;
    }

    timestamp_ms = HAL_GetTick();
    len = snprintf(line, sizeof(line), "%.6f,%.6f,%.6f,%.6f,%lu\n",
                   (double)q->w, (double)q->x, (double)q->y, (double)q->z,
                   (unsigned long)timestamp_ms);
    if (len <= 0)
    {
        return HAL_ERROR;
    }

    return uart_if_tx_blocking((const uint8_t *)line, (uint16_t)len, 50);
}
