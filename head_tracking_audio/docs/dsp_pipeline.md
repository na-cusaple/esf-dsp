# DSP Pipeline

## Inputs
- Mono WAV input file (soundfile)
- CIPIC HRIR dataset (.mat)

## Pipeline stages
1. Load input audio.
2. Downmix to mono if needed.
3. Optional resampling to target Fs (resample_poly).
4. Load CIPIC dataset: hrir_l/hrir_r, azimuths, elevations.
5. Convert quaternion to yaw/pitch.
6. Select HRIR by nearest elevation and nearest or interpolated azimuth.
7. Precompute HRIR FFT on update.
8. Audio callback: block read -> overlap-add FFT convolution -> stereo output.

## Block convolution
Let L be block size and M be HRIR length.
FFT size N = next power of two >= L + M - 1.
Overlap length = N - L.

## Interpolation
- Nearest elevation.
- Optional linear interpolation between nearest azimuths.

## Relevant modules
- python_host/audio/buffer_manager.py
- python_host/audio/audio_stream.py
- python_host/dsp/hrtf_loader.py
- python_host/dsp/hrtf_selector.py