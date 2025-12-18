import queue
import socket
import threading

from maix import uart


class ConnStatus:
    CONNECTED = True
    DISCONNECTED = False


class SocketConn:
    def __init__(self):
        self.conn = None
        self.status = ConnStatus.DISCONNECTED

    def connect(self, address) -> None:
        self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conn.connect(address)

        if self.conn:
            self.status = ConnStatus.CONNECTED

    def disconnect(self) -> None:
        if self.conn:
            self.conn.close()
            self.conn = None
            self.status = ConnStatus.DISCONNECTED

    def send(self, data: str) -> None:
        if self.conn:
            self.conn.sendall(data.encode() + b'\n')

    def recv(self, buffer_size=1024) -> str:
        if self.conn:
            return self.conn.recv(buffer_size).decode()
        return ''



class SerialConn:
    def __init__(self):
        self.conn = None
        self.thread = None
        self.data_queue = queue.Queue()
        self.status = ConnStatus.DISCONNECTED

    def connect(self, address) -> None:
        # here we can use the uart module from maix,
        # but for universality, we use serial module

        self.conn = uart.UART(port=address, baudrate=115200)

        if not (self.conn and self.conn.is_open):
            raise ConnectionError(f'Failed to open serial port: {address}')

        self.status = ConnStatus.CONNECTED
        self.thread = threading.Thread(target=self._read_loop, daemon=True)
        self.thread.start()

    def _read_loop(self):
        while self.status == ConnStatus.CONNECTED and self.conn:
            byte = self.conn.read()
            if not byte:
                continue
            self.data_queue.put(byte.decode())

    def disconnect(self) -> None:
        if self.conn and self.status:
            self.thread = None
            self.conn.close()
            self.conn = None
            self.status = ConnStatus.DISCONNECTED

    def send(self, data: str) -> None:
        if self.conn and self.conn.is_open:
            self.conn.write(data.encode() + b'\n')

    def recv(self) -> str:
        try:
            return self.data_queue.get(True, 10)
        except queue.Empty:
            return ''


if __name__ == '__main__':
    serial_conn = SerialConn()
    print('stage 1')
    serial_conn.connect('/dev/ttyS0')
    print('stage 2')
    serial_conn.send('DisableRobot()')
    print('stage 3')
    response = serial_conn.recv()
    print(f'Response: {response}')
    serial_conn.disconnect()
