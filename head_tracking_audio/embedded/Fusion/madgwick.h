#ifndef MADGWICK_H
#define MADGWICK_H

#include "quaternion.h"

void Madgwick_Init(float beta);
void Madgwick_Reset(void);
void Madgwick_UpdateIMU(float gx, float gy, float gz, float ax, float ay, float az, float dt);
Quaternion_t Madgwick_GetQuaternion(void);

#endif
