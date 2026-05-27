# Ghi chú độ trễ

## Thành phần
- UART delay: thời gian truyền từ device -> host.
- Queue age: thời gian từ khi host nhận đến khi worker xử lý.
- Chu kỳ cập nhật HRTF: 1 / HRTF_UPDATE_HZ (mặc định 20 ms).
- Audio buffer: block size / sample rate.
- Thời gian xử lý callback.

## Mô hình gần đúng
T_e2e = d_uart + d_queue + T_update + T_proc + T_buffer + T_dac

Trong đó:
- T_buffer = L / Fs
- T_update = 1 / f_update

## Theo dõi
LatencyMonitor theo dõi:
- thời gian callback so với budget (overrun)
- queue age
- uart delay (EMA time offset)

## Ghi chú
- Trường hợp xấu nhất, độ cũ của orientation nằm trong [0, 1/f_update].
- Nếu T_proc > T_buffer sẽ xảy ra underrun.