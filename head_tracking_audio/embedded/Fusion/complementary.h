#ifndef COMPLEMENTARY_H
#define COMPLEMENTARY_H

#include <stdint.h>

typedef struct
{
    float roll;
    float pitch;
    float yaw;
} Orientation_t;

void Complementary_Init(float alpha);
void Complementary_Reset(void);
void Complementary_Update(float ax, float ay, float az,
                          float gx, float gy, float gz,
                          float dt);
Orientation_t Complementary_GetOrientation(void);

#endif
