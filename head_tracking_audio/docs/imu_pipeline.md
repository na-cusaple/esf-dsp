# IMU Pipeline

## Sampling
- MPU6050 sampled at 200 Hz by timer tick (timer_if).
- imu_task_update reads raw accel/gyro.

## Calibration
- orientation_task_init averages 500 gyro samples to estimate bias.
- Bias is subtracted before conversion.

## Unit conversion
- Accelerometer: +/-4g => raw / 8192
- Gyro: +/-500 dps => (raw - bias) / 65.5, then deg to rad

## Madgwick update
- Madgwick_UpdateIMU with dt=0.005 s.
- Quaternion normalized internally.

## Streaming
- stream_task_send_quaternion formats ASCII CSV:
  qw,qx,qy,qz,timestamp_ms\n
- timestamp_ms from HAL_GetTick().

## Host consumption
- SerialReader reads lines and pushes (qw,qx,qy,qz,timestamp,host_time) into queue.
- OrientationWorker smooths quaternion (NLERP) and triggers HRTF updates.