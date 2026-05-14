# Architecture

## Overview
This project builds a head-tracked spatial audio pipeline:
- STM32 IMU -> quaternion stream over UART
- Python host -> orientation queue -> dynamic HRTF -> realtime stereo output

## Repository layout
- embedded/     STM32 firmware (BSP, Fusion, App, Comm)
- python_host/  Serial, DSP, audio, and visualization
- hrtf/         HRTF datasets (not included)
- audio/        Test audio clips
- docs/         Design notes and diagrams
- tools/        Benchmarks and calibration helpers

## Data flow
Embedded:
- MPU6050 sample @ 200 Hz
- Madgwick IMU fusion -> quaternion
- UART DMA @ 460800 baud

Host:
- Serial thread -> parse quaternion
- Orientation worker -> smoothing + HRTF update
- Audio callback -> overlap-add FFT convolution -> stereo output

## Thread model (Python)
- Serial thread: read UART, enqueue packets
- Orientation worker: consume queue, update HRTF filter
- Audio callback: render audio frames only (no blocking)

## Protocol
Quaternion packet (primary):
qw,qx,qy,qz,timestamp_ms\n

Debug packet (optional):
roll,pitch,yaw\n

## Timing targets
- IMU sample rate: 200 Hz
- UART baudrate: 460800+
- Audio sample rate: 48 kHz
- Block size: 256 (tune 1024/512/256/128)
- End-to-end latency target: < 30 ms

## HRTF datasets
Datasets are not committed. Suggested layout:
hrtf/
	cipic/
		subject_003/
			hrir_final_003.mat

The realtime and offline pipelines load a CIPIC .mat file directly.

## Realtime audio pipeline
Audio is processed in fixed blocks with overlap-add FFT convolution.
HRIR FFTs are precomputed on update to avoid per-callback FFT work.

## Benchmarks
Use tools/benchmark_audio.py to sweep block sizes and measure headroom.

## Known constraints
- Yaw will still drift without a magnetometer.
- HRTF interpolation is linear between nearest azimuths.
- Audio is resampled at load time if a target sample rate is requested.

