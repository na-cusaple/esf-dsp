# Hệ thống Head Tracking Audio

Pipeline âm thanh không gian thời gian thực có head tracking:
- Embedded (STM32 + IMU) -> hợp nhất cảm biến -> truyền UART
- Python host -> chọn HRTF -> FFT convolution -> audio output

## Bố cục repo
- embedded/         Source firmware STM32 (App/BSP/Fusion/Comm/Debug)
- python_host/      Runtime Python (serial, DSP, audio, visualization)
- docs/             Ghi chú kiến trúc và giao thức
- tools/            Hiệu chuẩn và đo hiệu năng
- hrtf/             Bộ dữ liệu HRTF (CIPIC, SOFA, HRIR)
- audio/            Tài nguyên âm thanh hoặc clip thử

## Kiến trúc
Luồng chạy (mục tiêu):
MPU6050 (200 Hz) -> imu_task -> Madgwick/Complementary -> Quaternion
-> UART DMA (460800 baud)
-> Python serial thread -> orientation queue -> audio engine
-> HRTF selector -> FFT convolution
-> sounddevice callback (48 kHz) -> headphones

## Đấu nối (STM32F401RE + MPU6050)
- SDA: PB9
- SCL: PB8
- VCC: 3.3V
- GND: GND

Ghi chú:
- Thêm điện trở kéo lên I2C (2.2k-4.7k) nếu module không có sẵn.
- UART dùng logic 3.3V và chung GND.

## Mục tiêu hiệu năng
- IMU sample rate: 200 Hz
- Mục tiêu độ trễ end-to-end: < 30 ms
- UART baudrate: 460800+
- Audio sample rate: 48 kHz
- Buffer size mục tiêu: 128-512 mẫu

## Luồng chạy
STM32:
```
[TIM2 IRQ]
	-> đọc IMU
	-> cập nhật fusion
	-> UART DMA
```

Python:
```
[Serial Thread]
	-> parse gói tin
	-> hàng đợi orientation

[Audio Thread]
	-> chọn HRTF
	-> convolution
	-> callback đầu ra
```

## Cài đặt
Python host (macOS/Linux):
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Tùy chọn (cài editable + entrypoints):
```bash
pip install -e .
pip install -e .[dev]
```

Ghi chú: requirements.txt dùng phiên bản pin để tái lập môi trường.
Ghi chú: sounddevice cần PortAudio; viewer 3D cần SDL/OpenGL qua pygame.

## Checklist chạy
1) Đặt file WAV mono trong audio/ (hoặc đường dẫn bạn muốn dùng)
2) Đặt file HRTF CIPIC .mat trong hrtf/
3) Xác định cổng serial (ví dụ: /dev/tty.usbmodemXXXX hoặc COM3)

Ghi chú: dữ liệu HRTF và audio test không kèm trong repo.

## Tài nguyên (tải về hoặc tạo)
HRTF (CIPIC, định dạng MAT):
- https://interface.cipic.ucdavis.edu/sound/hrtf.html
- Tải gói MAT và đặt các file subject_*.mat dưới hrtf/

Âm thanh thử (WAV mono):
- Dùng bất kỳ WAV mono nào của bạn, hoặc tạo tone ngắn:
```bash
python - <<'PY'
import numpy as np
import soundfile as sf

sr = 48000
t = np.linspace(0, 5.0, int(5.0 * sr), endpoint=False)
tone = 0.2 * np.sin(2 * np.pi * 440.0 * t)
sf.write("audio/test_tone.wav", tone.astype(np.float32), sr)
print("Đã ghi audio/test_tone.wav")
PY
```

Chạy realtime spatial audio:
```bash
python -m python_host.audio.spatializer --input audio/your_mono.wav --hrtf hrtf/subject_003.mat --port /dev/tty.usbmodemXXXX
```

Lệnh nếu đã cài:
```bash
hta-audio --input audio/your_mono.wav --hrtf hrtf/subject_003.mat --port /dev/tty.usbmodemXXXX
```

Chỉ hiển thị (không render audio):
```bash
python -m python_host.main --mode plot --port /dev/tty.usbmodemXXXX
```

Lệnh nếu đã cài:
```bash
hta-imu --mode plot --port /dev/tty.usbmodemXXXX
```

Ghi chú: HRIR CIPIC thường 44100 Hz; bộ nạp sẽ resample để khớp sample rate
của audio. Override bằng --hrtf-sr nếu cần.

Xem thêm: docs/runtime.md

## STM32CubeIDE (build embedded)
Khuyến nghị: để workspace CubeIDE tách khỏi repo.

1) Tạo workspace (ví dụ)
```bash
mkdir -p ~/stm32_ws
```

2) Tạo project STM32 mới trong CubeIDE
- File -> New -> STM32 Project
- Chọn MCU/board, đặt tên (ví dụ: head_tracking_audio_fw)

3) Liên kết source repo vào project CubeIDE
Trong Project Explorer:
- Right click project -> New -> Folder -> Advanced
- Link to alternate location -> chọn các đường dẫn:
	- head_tracking_audio/embedded/App
	- head_tracking_audio/embedded/BSP
	- head_tracking_audio/embedded/Fusion
	- head_tracking_audio/embedded/Comm
	- head_tracking_audio/embedded/Debug

4) Thêm include paths
Project -> Properties -> C/C++ General -> Paths and Symbols -> Includes
Thêm các thư mục như trên.

5) Cấu hình peripheral trong CubeMX
- I2C cho MPU6050
- UART để streaming
- TIM2 cho tick/interrupt (nếu dùng)

6) Build
- Build Debug hoặc Release trong CubeIDE
- Thư mục output (Debug/Release) đã được ignore trong .gitignore

## Bố cục build embedded
- embedded/Core     Startup, main, và HAL glue do CubeIDE tạo
- embedded/Drivers  CMSIS và HAL drivers (generated)
- embedded/App      Application tasks và state machine
- embedded/BSP      Board và sensor drivers (mpu6050, i2c_if, uart_if)
- embedded/Fusion   Complementary/Madgwick/quaternion utilities
- embedded/Comm     Serial protocol và packet format
- embedded/Debug    Debug logging và plotting hooks

Ghi chú: nếu đổi output build sang embedded/build, nhớ ignore trong .gitignore.

## Các giai đoạn phát triển
Giai đoạn 1:
- mpu6050.c, imu_task.c, serial_reader.py, realtime_plot.py

Giai đoạn 2:
- complementary.c

Giai đoạn 3:
- madgwick.c, quaternion.c

Giai đoạn 4:
- hrtf_loader.py, convolution.py, audio_stream.py

## Giao thức
Gói quaternion (ưu tiên):
qw,qx,qy,qz,timestamp\n

Gói debug (Euler):
roll,pitch,yaw\n

## Trạng thái hiện tại
- [ ] Đã tạo project STM32
- [ ] Đã xác minh giao tiếp I2C
- [ ] Đã kiểm tra WHO_AM_I của MPU6050
- [ ] Stream accelerometer thô
- [ ] Bộ lọc complementary
- [ ] Madgwick fusion
- [ ] Hiển thị serial bằng Python
- [ ] Audio HRTF realtime

## Hướng phát triển
- Pipeline chỉ dùng quaternion
- Hỗ trợ HRTF SOFA
- Nội suy động giữa các HRTF
- BLE streaming
- Tăng tốc DSP phía embedded
- GPU convolution

## Việc cần làm
- Bổ sung wiring/pin map và chi tiết MCU/board
- Thêm script chạy Python và test data
