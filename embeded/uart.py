from machine import UART


class UARTWrapper:
    """UART Communication Wrapper"""

    def __init__(self, uart_id, baud=115200, name='CAMERA'):
        """Initialize UART with given ID and baud rate."""
        self.name = name
        self.uart = UART(uart_id, baud)
        self.uart.init(baud, bits=8, parity=None, stop=1)

        print(f'Initialized UARTController on UART{uart_id} at baud {baud}')

    def send(self, data: str):
        """Send data over UART."""
        self.uart.write(data.encode() + b'\n')

        print(f'[ESP32] --> [{self.name}] | {data}')

    def recv(self) -> str:
        """Receive data over UART."""
        data = self.uart.readline()

        if not data:
            return ''

        data = data.decode().strip()
        print(f'[ESP32] <-- [{self.name}] | {data}')
        return data


if __name__ == '__main__':
    uart = UARTWrapper(2, 115200)

    uart.send('Hello UART from esp32!')

    uart.send('Testing UART communication.')

    while True:
        try:
            data = uart.recv()
            if data:
                print(f'Test received: {data}')
        except KeyboardInterrupt:
            break
