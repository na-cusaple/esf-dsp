#include "timer_if.h"

static volatile bool timer_tick = false;

HAL_StatusTypeDef timer_if_start(void)
{
    return HAL_TIM_Base_Start_IT(&TIMER_IF_HANDLE);
}

HAL_StatusTypeDef timer_if_stop(void)
{
    return HAL_TIM_Base_Stop_IT(&TIMER_IF_HANDLE);
}

void timer_if_on_tick_isr(void)
{
    timer_tick = true;
}

bool timer_if_consume_tick(void)
{
    if (!timer_tick)
    {
        return false;
    }
    timer_tick = false;
    return true;
}
