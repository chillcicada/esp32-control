from machine import UART


class UARTWrapper:
    """UART Communication Wrapper"""

    def __init__(self, uart_id, baud=115200):
        """Initialize UART with given ID and baud rate."""
        self.uart = UART(uart_id, baud)
        self.uart.init(baud, bits=8, parity=None, stop=1)

        print(f'Initialized UARTController on UART{uart_id} at baud {baud}')

    def send(self, buf):
        """Send data over UART."""
        self.uart.write(buf + b'\n')

        print(f'Sent data over UART: {buf}')

    def recv(self) -> str:
        """Receive data over UART."""
        buf = self.uart.read()

        if not buf:
            return None

        return buf.decode()


if __name__ == '__main__':
    uart = UARTWrapper(2, 115200)

    uart.send(b'Hello UART from esp32!')

    uart.send(b'Testing UART communication.')
    
    data = uart.recv()
    
    print('data:', data)

    while True:
        try:
            data = uart.recv()
            if data:
                print(f'Main received: {data.strip()}')
        except KeyboardInterrupt:
            break
