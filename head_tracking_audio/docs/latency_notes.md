# Latency Notes

## Components
- UART delay: device -> host transport time.
- Queue age: time from host receive to worker consume.
- HRTF update period: 1 / HRTF_UPDATE_HZ (default 20 ms).
- Audio buffer: block size / sample rate.
- Callback processing time.

## Rough model
T_e2e = d_uart + d_queue + T_update + T_proc + T_buffer + T_dac

Where:
- T_buffer = L / Fs
- T_update = 1 / f_update

## Monitoring
LatencyMonitor tracks:
- callback elapsed vs budget (overruns)
- queue age
- uart delay (EMA time offset)

## Notes
- Worst case orientation staleness is in [0, 1/f_update].
- If T_proc > T_buffer, underruns will occur.