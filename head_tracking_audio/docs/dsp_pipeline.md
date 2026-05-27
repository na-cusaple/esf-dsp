# Pipeline DSP

## Đầu vào
- File WAV mono (soundfile)
- Bộ dữ liệu HRIR CIPIC (.mat)

## Các bước pipeline
1. Load audio đầu vào.
2. Downmix về mono nếu cần.
3. Resample về Fs mục tiêu (resample_poly) nếu được yêu cầu.
4. Load bộ dữ liệu CIPIC: hrir_l/hrir_r, azimuth, elevation.
	- Nếu sample rate của dataset khác audio, HRIR sẽ được resample để khớp.
5. Đổi quaternion sang yaw/pitch.
6. Chọn HRIR theo elevation gần nhất và azimuth gần nhất hoặc nội suy.
7. Tính trước FFT của HRIR khi cập nhật.
8. Audio callback: đọc block -> overlap-add FFT convolution -> stereo output.

## Convolution theo block
Gọi L là block size, M là độ dài HRIR.
FFT size N = lũy thừa của 2 nhỏ nhất sao cho N >= L + M - 1.
Overlap length = N - L.

## Nội suy
- Elevation gần nhất.
- Nội suy tuyến tính giữa các azimuth gần nhất (tuỳ chọn).

## Module liên quan
- python_host/audio/buffer_manager.py
- python_host/audio/audio_stream.py
- python_host/dsp/hrtf_loader.py
- python_host/dsp/hrtf_selector.py
- python_host/config/audio_config.py