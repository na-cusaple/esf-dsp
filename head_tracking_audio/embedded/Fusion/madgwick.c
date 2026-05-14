#include "madgwick.h"
#include <math.h>

static Quaternion_t q = {1.0f, 0.0f, 0.0f, 0.0f};
static float madgwick_beta = 0.05f;

void Madgwick_Init(float beta)
{
    if (beta > 0.0f)
    {
        madgwick_beta = beta;
    }
    Madgwick_Reset();
}

void Madgwick_Reset(void)
{
    q.w = 1.0f;
    q.x = 0.0f;
    q.y = 0.0f;
    q.z = 0.0f;
}

Quaternion_t Madgwick_GetQuaternion(void)
{
    return q;
}

void Madgwick_UpdateIMU(float gx, float gy, float gz, float ax, float ay, float az, float dt)
{
    float recip_norm;
    float s1, s2, s3, s4;
    float q_dot1, q_dot2, q_dot3, q_dot4;
    float _2q1, _2q2, _2q3, _2q4;
    float _4q1, _4q2, _4q3;
    float _8q2, _8q3;
    float q1q1, q2q2, q3q3, q4q4;
    float q1 = q.w;
    float q2 = q.x;
    float q3 = q.y;
    float q4 = q.z;

    if (dt <= 0.0f)
    {
        return;
    }

    q_dot1 = 0.5f * (-q2 * gx - q3 * gy - q4 * gz);
    q_dot2 = 0.5f * (q1 * gx + q3 * gz - q4 * gy);
    q_dot3 = 0.5f * (q1 * gy - q2 * gz + q4 * gx);
    q_dot4 = 0.5f * (q1 * gz + q2 * gy - q3 * gx);

    if (!((ax == 0.0f) && (ay == 0.0f) && (az == 0.0f)))
    {
        recip_norm = sqrtf(ax * ax + ay * ay + az * az);
        if (recip_norm > 0.0f)
        {
            ax /= recip_norm;
            ay /= recip_norm;
            az /= recip_norm;
        }

        _2q1 = 2.0f * q1;
        _2q2 = 2.0f * q2;
        _2q3 = 2.0f * q3;
        _2q4 = 2.0f * q4;
        _4q1 = 4.0f * q1;
        _4q2 = 4.0f * q2;
        _4q3 = 4.0f * q3;
        _8q2 = 8.0f * q2;
        _8q3 = 8.0f * q3;
        q1q1 = q1 * q1;
        q2q2 = q2 * q2;
        q3q3 = q3 * q3;
        q4q4 = q4 * q4;

        s1 = _4q1 * q3q3 + _2q3 * ax + _4q1 * q2q2 - _2q2 * ay;
        s2 = _4q2 * q4q4 - _2q4 * ax + 4.0f * q1q1 * q2 - _2q1 * ay - _4q2 + _8q2 * q2q2 + _8q2 * q3q3 + _4q2 * az;
        s3 = 4.0f * q1q1 * q3 + _2q1 * ax + _4q3 * q4q4 - _2q4 * ay - _4q3 + _8q3 * q2q2 + _8q3 * q3q3 + _4q3 * az;
        s4 = 4.0f * q2q2 * q4 - _2q2 * ax + 4.0f * q3q3 * q4 - _2q3 * ay;

        recip_norm = sqrtf(s1 * s1 + s2 * s2 + s3 * s3 + s4 * s4);
        if (recip_norm > 0.0f)
        {
            s1 /= recip_norm;
            s2 /= recip_norm;
            s3 /= recip_norm;
            s4 /= recip_norm;
        }

        q_dot1 -= madgwick_beta * s1;
        q_dot2 -= madgwick_beta * s2;
        q_dot3 -= madgwick_beta * s3;
        q_dot4 -= madgwick_beta * s4;
    }

    q1 += q_dot1 * dt;
    q2 += q_dot2 * dt;
    q3 += q_dot3 * dt;
    q4 += q_dot4 * dt;

    recip_norm = sqrtf(q1 * q1 + q2 * q2 + q3 * q3 + q4 * q4);
    if (recip_norm > 0.0f)
    {
        q1 /= recip_norm;
        q2 /= recip_norm;
        q3 /= recip_norm;
        q4 /= recip_norm;
    }

    q.w = q1;
    q.x = q2;
    q.y = q3;
    q.z = q4;
}
