# Pipeline IMU

## Lấy mẫu
- MPU6050 lấy mẫu 200 Hz bằng timer tick (timer_if).
- imu_task_update đọc accel/gyro thô.

## Hiệu chuẩn
- orientation_task_init lấy trung bình 500 mẫu gyro để ước lượng bias.
- Bias được trừ trước khi đổi đơn vị.

## Chuyển đổi đơn vị
- Accelerometer: +/-4g => raw / 8192
- Gyro: +/-500 dps => (raw - bias) / 65.5, sau đó đổi từ độ sang rad

## Cập nhật Madgwick
- Madgwick_UpdateIMU với dt=0.005 s.
- Quaternion được chuẩn hóa nội bộ.

## Streaming
- stream_task_send_quaternion format ASCII CSV:
  qw,qx,qy,qz,timestamp_ms\n
- timestamp_ms lấy từ HAL_GetTick().

## Host xử lý
- SerialReader đọc dòng và đẩy (qw,qx,qy,qz,timestamp,host_time) vào queue.
- OrientationWorker làm mượt quaternion (NLERP) và kích hoạt cập nhật HRTF.