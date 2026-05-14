#ifndef QUATERNION_H
#define QUATERNION_H

typedef struct
{
    float w;
    float x;
    float y;
    float z;
} Quaternion_t;

void Quaternion_Normalize(Quaternion_t *q);
void Quaternion_ToEuler(const Quaternion_t *q, float *roll, float *pitch, float *yaw);

#endif
