# Giao thức Serial

## Tổng quan
Firmware embedded stream các mẫu orientation dạng quaternion qua UART theo dòng CSV ASCII.
Python host mong đợi định dạng này trong python_host/serial/parser.py.

## Định dạng gói (quaternion)
qw,qx,qy,qz,timestamp_ms\n

- qw,qx,qy,qz: các thành phần quaternion đơn vị (float, đã chuẩn hóa trên MCU).
- timestamp_ms: device tick theo mili giây (uint32 từ HAL_GetTick).
- Các trường được format với 6 chữ số thập phân, kết thúc bằng newline.

Ví dụ:
0.998532,0.012345,-0.033210,0.045678,1234567

## Gói debug (tuỳ chọn)
roll,pitch,yaw\n

- Góc Euler theo độ.
- Không được parser hiện tại đọc (nó bỏ qua các dòng có ít hơn 5 trường).

## Truyền tải
- UART baudrate: mặc định 460800.
- ASCII CSV, không checksum.

## Ghi chú
- Nếu format gói thay đổi, cập nhật parser.py và các tool liên quan.
- Khi hàng đợi host đầy, mẫu cũ sẽ bị drop để giữ độ trễ thấp.