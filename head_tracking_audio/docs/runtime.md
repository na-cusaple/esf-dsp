# Hướng dẫn chạy

## Yêu cầu hệ thống
- Python 3.10+
- PortAudio (cần cho sounddevice)
- SDL/OpenGL (chỉ cho viewer 3D)

## Cài đặt
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Cài editable (thêm entrypoints):
```bash
pip install -e .
pip install -e .[dev]
```

## Tài nguyên
- audio/: file WAV mono
- hrtf/: file CIPIC subject_*.mat

Ghi chú: HRIR CIPIC thường 44100 Hz. Bộ nạp sẽ resample theo sample rate
của audio. Override bằng --hrtf-sr nếu cần.

## Audio không gian realtime
```bash
python -m python_host.audio.spatializer \
  --input audio/your_mono.wav \
  --hrtf hrtf/subject_003.mat \
  --port /dev/tty.usbmodemXXXX
```

Nếu đã cài:
```bash
hta-audio --input audio/your_mono.wav --hrtf hrtf/subject_003.mat --port /dev/tty.usbmodemXXXX
```

Flag hữu ích:
- --block-size 256
- --sample-rate 48000
- --hrtf-sr 44100
- --interpolate
- --print-stats

## Hiển thị IMU
```bash
python -m python_host.main --mode plot --port /dev/tty.usbmodemXXXX
python -m python_host.main --mode cube --port /dev/tty.usbmodemXXXX
```

Nếu đã cài:
```bash
hta-imu --mode plot --port /dev/tty.usbmodemXXXX
```

## Render offline
```bash
python -m python_host.dsp.spatializer \
  --input audio/your_mono.wav \
  --output audio/out_stereo.wav \
  --hrtf hrtf/subject_003.mat \
  --yaw -90
```

## Đo hiệu năng
```bash
python tools/benchmark_audio.py --input audio/your_mono.wav --hrtf hrtf/subject_003.mat
```
