#include "app_main.h"
#include "timer_if.h"
#include "uart_if.h"
#include "imu_task.h"

HAL_StatusTypeDef app_main_init(void)
{
    HAL_StatusTypeDef status = timer_if_start();
    if (status != HAL_OK)
    {
        return status;
    }

    return imu_task_init();
}

void app_main_loop(void)
{
    imu_task_update();
}

void app_main_on_timer_tick(void)
{
    timer_if_on_tick_isr();
}

void app_main_on_uart_tx_complete(UART_HandleTypeDef *huart)
{
    if (huart == &UART_IF_HANDLE)
    {
        uart_if_on_tx_complete();
    }
}
