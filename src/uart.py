from machine import UART


class UARTWrapper:
    def __init__(self, uart_id, baud=115200):
        self.uart = UART(uart_id, baud)
        self.uart.init(baud, bits=8, parity=None, stop=1)

        print(f'Initialized UARTController on UART{uart_id} at baud {baud}')

    def send(self, buf):
        self.uart.write(buf)
        print(f'Sent data over UART: {buf}')

    def recv(self):
        if self.uart.any() <= 0:
            print('No data available to read from UART')
            return None

        buf = self.uart.read()

        if not buf:
            print('Received empty data from UART')
            return None

        print(f'Received data over UART: {buf}')
