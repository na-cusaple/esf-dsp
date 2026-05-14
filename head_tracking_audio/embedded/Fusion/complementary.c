#include "complementary.h"
#include <math.h>

#define RAD_TO_DEG 57.2957795f

static Orientation_t orientation;
static float filter_alpha = 0.98f;

void Complementary_Init(float alpha)
{
    if (alpha > 0.0f && alpha < 1.0f)
    {
        filter_alpha = alpha;
    }
    Complementary_Reset();
}

void Complementary_Reset(void)
{
    orientation.roll = 0.0f;
    orientation.pitch = 0.0f;
    orientation.yaw = 0.0f;
}

void Complementary_Update(float ax, float ay, float az,
                          float gx, float gy, float gz,
                          float dt)
{
    float roll_acc;
    float pitch_acc;
    float roll_gyro;
    float pitch_gyro;

    if (dt <= 0.0f)
    {
        return;
    }

    roll_acc = atan2f(ay, az) * RAD_TO_DEG;
    pitch_acc = atan2f(-ax, sqrtf(ay * ay + az * az)) * RAD_TO_DEG;

    roll_gyro = orientation.roll + gx * dt;
    pitch_gyro = orientation.pitch + gy * dt;

    orientation.roll = filter_alpha * roll_gyro + (1.0f - filter_alpha) * roll_acc;
    orientation.pitch = filter_alpha * pitch_gyro + (1.0f - filter_alpha) * pitch_acc;
    orientation.yaw += gz * dt;
}

Orientation_t Complementary_GetOrientation(void)
{
    return orientation;
}
