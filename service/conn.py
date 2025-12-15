class ConnStatus:
    CONNECTED = True
    DISCONNECTED = False


class SocketConn:
    def __init__(self):
        self.conn = None
        self.status = ConnStatus.DISCONNECTED

    def connect(self, address) -> None:
        import socket

        self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conn.connect(address)

        if self.conn:
            self.status = ConnStatus.CONNECTED

    def disconnect(self) -> None:
        if self.conn:
            self.conn.close()
            self.conn = None
            self.status = ConnStatus.DISCONNECTED

    def send(self, data: bytes) -> None:
        if self.conn:
            self.conn.sendall(data + b'\n')

    def recv(self, buffer_size=1024) -> str:
        if self.conn:
            # return self.conn.recv(buffer_size).decode()
            return self.conn.recv(buffer_size).decode()
        return ''

    def settimeout(self, timeout: float) -> None:
        if self.conn:
            self.conn.settimeout(timeout)


class SerialConn:
    def __init__(self):
        self.conn = None
        self.status = ConnStatus.DISCONNECTED

    def connect(self, address) -> None:
        # here we can use the uart module from maix,
        # but for universality, we use serial module
        import serial

        self.conn = serial.Serial(port=address, baudrate=115200)

        if self.conn and self.conn.is_open:
            self.status = ConnStatus.CONNECTED

    def disconnect(self) -> None:
        if self.status:
            self.conn.close()
            self.conn = None
            self.status = ConnStatus.DISCONNECTED

    def send(self, data: bytes) -> None:
        if self.conn and self.conn.is_open:
            self.conn.write(data + b'\n')

    def recv(self) -> str:
        if self.conn and self.conn.is_open:
            return self.conn.readline().decode()
        return ''

    def settimeout(self, timeout: float) -> None:
        if self.conn and self.conn.is_open:
            self.conn.timeout = timeout


if __name__ == '__main__':
    serial_conn = SerialConn()
    print('stage 1')
    serial_conn.connect('/dev/ttyS0')
    serial_conn.settimeout(10)
    print('stage 2')
    serial_conn.send(b'DisableRobot()')
    print('stage 3')
    response = serial_conn.recv(1024)
    print(f'Response: {response}')
