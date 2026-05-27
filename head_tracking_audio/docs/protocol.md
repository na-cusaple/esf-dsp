# Serial Protocol

## Overview
The embedded firmware streams quaternion orientation samples over UART as an ASCII CSV line.
The Python host expects this format in python_host/serial/parser.py.

## Packet format (quaternion)
qw,qx,qy,qz,timestamp_ms\n

- qw,qx,qy,qz: unit quaternion components (float, normalized on the MCU).
- timestamp_ms: device tick in milliseconds (uint32 from HAL_GetTick).
- Fields are formatted with 6 decimal digits, newline terminated.

Example:
0.998532,0.012345,-0.033210,0.045678,1234567

## Debug packet (optional)
roll,pitch,yaw\n

- Euler angles in degrees.
- Not parsed by the current host parser (it will ignore lines with fewer than 5 fields).

## Transport
- UART baudrate: 460800 by default.
- ASCII CSV, no checksum.

## Notes
- If the packet format changes, update parser.py and any tooling.
- When the host queue is full, old samples are dropped to keep latency low.