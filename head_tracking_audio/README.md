# Head Tracking Audio

Real-time head tracking and spatial audio pipeline:
- Embedded (STM32 + IMU) -> sensor fusion -> UART stream
- Python host -> HRTF select -> FFT convolution -> audio output

## Repo layout
- embedded/         STM32 firmware source (App/BSP/Fusion/Comm/Debug)
- python_host/      Python runtime (serial, DSP, audio, visualization)
- docs/             Architecture and protocol notes
- tools/            Calibration and benchmarks
- hrtf/             HRTF datasets (CIPIC, SOFA, HRIR)
- audio/            Audio assets or test clips

## Architecture
Runtime flow (target):
MPU6050 (200 Hz) -> imu_task -> Madgwick/Complementary -> Quaternion
-> UART DMA (460800 baud)
-> Python serial thread -> orientation queue -> audio engine
-> HRTF selector -> FFT convolution
-> sounddevice callback (48 kHz) -> headphones

## Wiring (STM32F401RE + MPU6050)
- SDA: PB9
- SCL: PB8
- VCC: 3.3V
- GND: GND

Notes:
- Add I2C pull-ups (2.2k-4.7k) if the module does not include them.
- UART uses 3.3V logic with common GND.

## Performance targets
- IMU sample rate: 200 Hz
- End-to-end latency target: < 30 ms
- UART baudrate: 460800+
- Audio sample rate: 48 kHz
- Buffer size target: 128-512 samples

## Runtime threads
STM32:
```
[TIM2 IRQ]
	-> read IMU
	-> fusion update
	-> UART DMA
```

Python:
```
[Serial Thread]
	-> parse packet
	-> orientation queue

[Audio Thread]
	-> HRTF selection
	-> convolution
	-> output callback
```

## Setup
Python host (macOS/Linux):
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Note: requirements.txt uses pinned versions for reproducibility.

## Run checklist
1) Place a mono WAV file under audio/ (or any path you will reference)
2) Place a CIPIC .mat HRTF file under hrtf/
3) Identify your serial port (e.g. /dev/tty.usbmodemXXXX or COM3)

Note: HRTF datasets and test audio are not bundled with this repo.

## Assets (download or generate)
HRTF (CIPIC, MAT format):
- https://interface.cipic.ucdavis.edu/sound/hrtf.html
- Download the MAT archive and place subject_*.mat files under hrtf/

Test audio (mono WAV):
- Use any mono WAV you own, or generate a short tone:
```bash
python - <<'PY'
import numpy as np
import soundfile as sf

sr = 48000
t = np.linspace(0, 5.0, int(5.0 * sr), endpoint=False)
tone = 0.2 * np.sin(2 * np.pi * 440.0 * t)
sf.write("audio/test_tone.wav", tone.astype(np.float32), sr)
print("Wrote audio/test_tone.wav")
PY
```

Run entry (realtime spatial audio):
```bash
python -m python_host.audio.spatializer --input audio/your_mono.wav --hrtf hrtf/subject_003.mat --port /dev/tty.usbmodemXXXX
```

Visualization only (no audio rendering):
```bash
python -m python_host.main --mode plot --port /dev/tty.usbmodemXXXX
```

## STM32CubeIDE (embedded build)
Recommended: keep CubeIDE workspace separate from the repo.

1) Create workspace (example)
```bash
mkdir -p ~/stm32_ws
```

2) Create a new STM32 project in CubeIDE
- File -> New -> STM32 Project
- Select MCU/board, name it (example: head_tracking_audio_fw)

3) Link repo sources into the CubeIDE project
In Project Explorer:
- Right click project -> New -> Folder -> Advanced
- Link to alternate location -> select repo paths:
	- head_tracking_audio/embedded/App
	- head_tracking_audio/embedded/BSP
	- head_tracking_audio/embedded/Fusion
	- head_tracking_audio/embedded/Comm
	- head_tracking_audio/embedded/Debug

4) Add include paths
Project -> Properties -> C/C++ General -> Paths and Symbols -> Includes
Add the same folders listed above.

5) Configure peripherals in CubeMX
- I2C for MPU6050
- UART for streaming
- TIM2 for tick/interrupt (if used)

6) Build
- Build Debug or Release in CubeIDE
- Output directories (Debug/Release) are ignored by .gitignore

## Embedded build layout
- embedded/Core     CubeIDE generated startup, main, and HAL glue
- embedded/Drivers  CMSIS and HAL drivers (generated)
- embedded/App      Application tasks and state machine
- embedded/BSP      Board and sensor drivers (mpu6050, i2c_if, uart_if)
- embedded/Fusion   Complementary/Madgwick/quaternion utilities
- embedded/Comm     Serial protocol and packet format
- embedded/Debug    Debug logging and plotting hooks

Note: if you switch build output to embedded/build, keep it ignored in .gitignore.

## Development phases
Phase 1:
- mpu6050.c, imu_task.c, serial_reader.py, realtime_plot.py

Phase 2:
- complementary.c

Phase 3:
- madgwick.c, quaternion.c

Phase 4:
- hrtf_loader.py, convolution.py, audio_stream.py

## Protocol
Quaternion packet (preferred):
qw,qx,qy,qz,timestamp\n

Debug packet (Euler):
roll,pitch,yaw\n

## Current status
- [ ] STM32 project created
- [ ] I2C communication verified
- [ ] MPU6050 WHO_AM_I verified
- [ ] Raw accelerometer stream
- [ ] Complementary filter
- [ ] Madgwick fusion
- [ ] Python serial visualization
- [ ] Realtime HRTF audio

## Future upgrades
- Quaternion-only pipeline
- SOFA HRTF support
- Dynamic interpolation between HRTFs
- BLE streaming
- Embedded DSP acceleration
- GPU convolution

## TODO
- Fill wiring/pin map and MCU/board details
- Define serial packet schema and sample rate
- Add Python run scripts and test data
