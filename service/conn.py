from abc import ABC, abstractmethod


class ConnStatus:
    CONNECTED = True
    DISCONNECTED = False


class ConnInterface(ABC):
    @abstractmethod
    def connect(self, address) -> None:
        """Establish a connection to the specified address."""
        pass

    @abstractmethod
    def disconnect(self) -> None:
        """Terminate the current connection."""
        pass

    @abstractmethod
    def send(self, data: bytes) -> None:
        """Send data over the connection."""
        pass

    @abstractmethod
    def recv(self, buffer_size: int) -> str:
        """Receive decoded data from the connection."""
        pass

    @abstractmethod
    def settimeout(self, timeout: float) -> None:
        """Set the timeout for the connection."""
        pass

    @property
    @abstractmethod
    def status(self) -> bool:
        """Get the current connection status."""
        pass


class SocketConn(ConnInterface):
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

    def recv(self, buffer_size: int) -> str:
        if self.conn:
            return self.conn.recv(buffer_size).decode()
        return ''

    def settimeout(self, timeout: float) -> None:
        if self.conn:
            self.conn.settimeout(timeout)


class SerialConn(ConnInterface):
    def __init__(self):
        self.conn = None
        self.status = ConnStatus.DISCONNECTED

    def connect(self, address) -> None:
        import serial

        self.conn = serial.Serial(port=address, baudrate=9600)

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

    def recv(self, buffer_size: int) -> str:
        if self.conn and self.conn.is_open:
            return self.conn.read(buffer_size).decode()
        return ''

    def settimeout(self, timeout: float) -> None:
        if self.conn and self.conn.is_open:
            self.conn.timeout = timeout
