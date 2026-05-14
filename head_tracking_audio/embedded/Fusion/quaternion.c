#include "quaternion.h"
#include <math.h>

void Quaternion_Normalize(Quaternion_t *q)
{
    float norm;
    if (q == NULL)
    {
        return;
    }

    norm = sqrtf(q->w * q->w + q->x * q->x + q->y * q->y + q->z * q->z);
    if (norm <= 0.0f)
    {
        return;
    }

    q->w /= norm;
    q->x /= norm;
    q->y /= norm;
    q->z /= norm;
}

void Quaternion_ToEuler(const Quaternion_t *q, float *roll, float *pitch, float *yaw)
{
    float sinr_cosp;
    float cosr_cosp;
    float sinp;
    float siny_cosp;
    float cosy_cosp;

    if (q == NULL || roll == NULL || pitch == NULL || yaw == NULL)
    {
        return;
    }

    sinr_cosp = 2.0f * (q->w * q->x + q->y * q->z);
    cosr_cosp = 1.0f - 2.0f * (q->x * q->x + q->y * q->y);
    *roll = atan2f(sinr_cosp, cosr_cosp);

    sinp = 2.0f * (q->w * q->y - q->z * q->x);
    if (fabsf(sinp) >= 1.0f)
    {
        *pitch = copysignf((float)M_PI / 2.0f, sinp);
    }
    else
    {
        *pitch = asinf(sinp);
    }

    siny_cosp = 2.0f * (q->w * q->z + q->x * q->y);
    cosy_cosp = 1.0f - 2.0f * (q->y * q->y + q->z * q->z);
    *yaw = atan2f(siny_cosp, cosy_cosp);
}
