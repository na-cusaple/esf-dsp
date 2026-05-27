# Kiến trúc

## Tổng quan
Dự án xây dựng pipeline âm thanh không gian có head tracking:
- STM32 IMU -> stream quaternion qua UART
- Python host -> orientation queue -> HRTF động -> đầu ra stereo thời gian thực

## Bố cục repo
- embedded/     Firmware STM32 (BSP, Fusion, App, Comm)
- python_host/  Serial, DSP, audio và hiển thị
- hrtf/         Bộ dữ liệu HRTF (không kèm trong repo)
- audio/        Clip âm thanh thử
- docs/         Ghi chú thiết kế và sơ đồ
- tools/        Benchmark và công cụ hiệu chuẩn

## Luồng dữ liệu
Embedded:
- MPU6050 lấy mẫu 200 Hz
- Madgwick IMU fusion -> quaternion
- UART DMA @ 460800 baud

Host:
- Serial thread -> parse quaternion
- Orientation worker -> làm mượt + cập nhật HRTF
- Audio callback -> overlap-add FFT convolution -> đầu ra stereo

## Mô hình luồng (Python)
- Serial thread: đọc UART, đưa gói vào queue
- Orientation worker: lấy queue, cập nhật filter HRTF
- Audio callback: chỉ render frame audio (không block)

## Giao thức
Gói quaternion (chính):
qw,qx,qy,qz,timestamp_ms\n

Gói debug (tuỳ chọn):
roll,pitch,yaw\n

## Mục tiêu thời gian
- IMU sample rate: 200 Hz
- UART baudrate: 460800+
- Audio sample rate: 48 kHz
- Block size: 256 (tinh chỉnh 1024/512/256/128)
- Mục tiêu độ trễ end-to-end: < 30 ms

## Bộ dữ liệu HRTF
Dữ liệu không được commit. Bố cục gợi ý:
hrtf/
	cipic/
		subject_003/
			hrir_final_003.mat

Pipeline realtime và offline đọc trực tiếp file CIPIC .mat.

## Pipeline audio thời gian thực
Audio được xử lý theo block cố định bằng overlap-add FFT convolution.
FFT của HRIR được tính trước khi cập nhật để tránh FFT trong callback.
Nếu sample rate của HRTF khác audio, HRIR sẽ được resample khi load.

## Đo hiệu năng
Dùng tools/benchmark_audio.py để quét block size và đo headroom.

## Giới hạn đã biết
- Yaw vẫn drift nếu không có magnetometer.
- Nội suy HRTF tuyến tính theo azimuth gần nhất.
- Audio được resample khi load nếu có target sample rate.
- Cập nhật HRTF thay convolver có thể gây click; có thể giảm bằng crossfade.

