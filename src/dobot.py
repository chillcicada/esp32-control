"""
Dobot TCP Wrapper Based on Function Signatures

@author: chillcicada
@license: MIT
"""

from functools import wraps
from inspect import signature
from socket import AF_INET, SOCK_DGRAM, socket

# Use type aliases for better readability
type DobotResponse = tuple[int, list, str]
type DobotResponse2 = tuple[int, list, str]


class DobotErrorCode:
    """Dobot error codes."""

    SUCCESS = 0
    EXECUTION_FAILED = -1
    ALARMED = -2
    EMERGENCY_STOP = -3
    POWER_OFF = -4
    SCRIPT_RUNNING = -5
    MISMATCHED = -6
    SCRIPT_PAUSED = -7
    AUTH_EXPIRED = -8

    CMD_NOT_FOUND = -10000
    PARAM_NUM_ERROR = -20000
    REQ_PARAM_TYPE_ERROR = -30000  # -3000X
    REQ_PARAM_OUT_OF_RANGE = -40000  # -4000X
    OPT_PARAM_TYPE_ERROR = -50000  # -5000X
    OPT_PARAM_OUT_OF_RANGE = -60000  # -6000X


class Dobot:
    def __init__(self, ip='192.168.5.1', port=29999):
        self.ip = ip
        self.port = port
        self.socket = None

        self.enableDebug = False

    # region core

    def parse(self, data: str, handler=None) -> DobotResponse:
        parts = data.strip().split(',')

        if not parts:
            self.error('Received empty response.')
            return DobotErrorCode.EXECUTION_FAILED, [], ''

        try:
            err = int(parts[0])
            params = [float(p) if '.' in p else int(p) for p in parts[1:-1]]
            msg = parts[-1] if len(parts) > 1 else ''

            if handler:
                return handler(err, params, msg)

            return err, params, msg

        except ValueError as e:
            self.error(f'Parsing response failed: {e}')
            return DobotErrorCode.EXECUTION_FAILED, [], ''

    @staticmethod
    def send(handler=None):
        def decorator(func):
            @wraps(func)
            def sender(self: 'Dobot', *args, **kwargs) -> DobotResponse:
                if not self.socket:
                    self.error('Not connected to Dobot.')
                    raise ConnectionError('Not connected to Dobot.')

                sign = signature(func)
                return_type = signature(func).return_annotation

                bound = sign.bind(self, *args, **kwargs)
                bound.apply_defaults()

                if return_type == DobotResponse:
                    params = [
                        f'{k.removeprefix("_")}={v}' if k.startswith('_') else str(v)
                        for k, v in bound.arguments.items()
                        if k != 'self' and v is not None
                    ]
                    command = f'{func.__name__}({",".join(params)})'
                elif return_type == DobotResponse2:
                    params = func(self, *args, **kwargs)
                    command = f'{func.__name__}({params})'
                else:
                    self.error(f'Invalid return type for {func.__name__}: {return_type}')
                    raise TypeError(f'Invalid return type for {func.__name__}: {return_type}')

                self.socket.sendall(command.encode() + b'\n')
                self.debug(f'Sent command: {command}')

                return self.parse(self.socket.recv(1024).decode(), handler)

            return sender

        return decorator

    def debug(self, str: str) -> None:
        if self.enableDebug:
            print(f'[Dobot DEBUG] {str}')

    def error(self, str: str) -> None:
        print(f'[Dobot ERROR] {str}')

    def connect(self, timeout=2) -> None:
        try:
            self.debug(f'Connecting to {self.ip}:{self.port} with timeout {timeout}s')
            self.socket = socket(AF_INET, SOCK_DGRAM)
            self.socket.settimeout(timeout)
            self.socket.connect((self.ip, self.port))
            self.debug('Connection established.')

        except Exception as e:
            self.error(f'Connection failed: {e}')
            self.socket = None

    def disconnect(self) -> None:
        if not self.socket:
            self.debug('No active connection to disconnect.')
            return

        self.debug('Disconnecting...')
        self.socket.close()
        self.socket = None
        self.debug('Disconnected.')

    # endregion
    # --------------
    # region control

    @send()
    def RequestControl(self) -> DobotResponse:
        pass

    @send()
    def PowerON(self) -> DobotResponse:
        pass

    @send()
    def EnableRobot(
        self,
        load: float = None,
        centerX: float = None,
        centerY: float = None,
        centerZ: float = None,
        isCheck: int = None,
    ) -> DobotResponse:
        pass

    @send()
    def DisableRobot(self) -> DobotResponse:
        pass

    @send()
    def ClearError(self) -> DobotResponse:
        pass

    @send()
    def RunScript(self, projectName: str) -> DobotResponse:
        pass

    @send()
    def Stop(self) -> DobotResponse:
        pass

    @send()
    def Pause(self) -> DobotResponse:
        pass

    @send()
    def Continue(self) -> DobotResponse:
        pass

    @send()
    def EmergencyStop(self, mode: str) -> DobotResponse:
        pass

    @send()
    def BrakeControl(self, axisID: int, value: int) -> DobotResponse:
        pass

    @send()
    def StartDrag(self) -> DobotResponse:
        pass

    @send()
    def StopDrag(self) -> DobotResponse:
        pass

    # endregion
    # ---------------
    # region settings

    @send()
    def SpeedFactor(self, ratio: int = 0) -> DobotResponse:
        pass

    @send()
    def User(self, index: int) -> DobotResponse:
        pass

    @send()
    def SetUser(self, index: int, value: str, type: int = 0) -> DobotResponse:
        pass

    @send()
    def CalcUser(self, index: int, matrix: int, offset: int) -> DobotResponse:
        pass

    @send()
    def Tool(self, index: int = 0) -> DobotResponse:
        pass

    @send()
    def SetTool(self, index: int, value: str, type: int = 0) -> DobotResponse:
        pass

    @send()
    def CalcTool(self, index: int, matrix: int, offset: str) -> DobotResponse:
        pass

    @send()
    def SetPayload(self, load_or_name: str | float, x: float = None, y: float = None, z: float = None) -> DobotResponse:
        pass

    @send()
    def AccJ(self, R: int = 100) -> DobotResponse:
        pass

    @send()
    def AccL(self, R: int = 100) -> DobotResponse:
        pass

    @send()
    def VelJ(self, R: int = 100) -> DobotResponse:
        pass

    @send()
    def VelL(self, R: int = 100) -> DobotResponse:
        pass

    @send()
    def CP(self, R: int = 0) -> DobotResponse:
        pass

    @send()
    def SetCollisionLevel(self, level: int) -> DobotResponse:
        pass

    @send()
    def SetBackDistance(self, distance: float) -> DobotResponse:
        pass

    @send()
    def SetPostCollisionMode(self, mode: int) -> DobotResponse:
        pass

    @send()
    def DragSensitivity(self, index: int, value: int) -> DobotResponse:
        pass

    @send()
    def EnableSafeSkin(self, status: int) -> DobotResponse:
        pass

    @send()
    def SetSafeSkin(self, part: int, status: int) -> DobotResponse:
        pass

    @send()
    def SetSafeWallEnable(self, index: int, value: int) -> DobotResponse:
        pass

    @send()
    def SetWorkZoneEnable(self, index: int, value: int) -> DobotResponse:
        pass

    # endregion
    # ------------------
    # region calculation

    @send()
    def RobotMode(self) -> DobotResponse:
        pass

    @send()
    def PositiveKin(
        self, J1: float, J2: float, J3: float, J4: float, J5: float, J6: float, _user: int = 0, _tool: int = 0
    ) -> DobotResponse:
        pass

    @send()
    def InverseKin(
        self,
        X: float,
        Y: float,
        Z: float,
        Rx: float,
        Ry: float,
        Rz: float,
        _useJointNear: int = 0,
        _JointNear: str = '',
        _user: int = 0,
        _tool: int = 0,
    ) -> DobotResponse:
        pass

    @send()
    def GetAngle(self) -> DobotResponse:
        pass

    @send()
    def GetPose(self, _user: int = 0, _tool: int = 0) -> DobotResponse:
        pass

    @send()
    def GetErrorID(self) -> DobotResponse:
        pass

    @send()
    def Create1DTray(self, Trayname: str, Count: str, Points: str) -> DobotResponse:
        pass

    @send()
    def Create2DTray(self, Trayname: str, Count: str, Points: str) -> DobotResponse:
        pass

    @send()
    def Create3DTray(self, Trayname: str, Count: str, Points: str) -> DobotResponse:
        pass

    @send()
    def GetTrayPoint(self, Trayname: str, index: int) -> DobotResponse:
        pass

    # endregion
    # ---------
    # region io

    @send()
    def DO(self, index: int, status: int, time: int = None) -> DobotResponse:
        pass

    @send()
    def DOInstant(self, index: int, status: int) -> DobotResponse:
        pass

    @send()
    def GetDO(self, index: int) -> DobotResponse:
        pass

    @send()
    def DOGroup(self, values: str) -> DobotResponse:
        pass

    @send()
    def GetDOGroup(self, values: str) -> DobotResponse:
        pass

    @send()
    def ToolDO(self, index: int, status: int) -> DobotResponse:
        pass

    @send()
    def ToolDOInstant(self, index: int, status: int) -> DobotResponse:
        pass

    @send()
    def GetToolDO(self, index: int) -> DobotResponse:
        pass

    @send()
    def AO(self, index: int, value: int) -> DobotResponse:
        pass

    @send()
    def AOInstant(self, index: int, value: int) -> DobotResponse:
        pass

    @send()
    def GetAO(self, index: int) -> DobotResponse:
        pass

    @send()
    def DI(self, index: int) -> DobotResponse:
        pass

    @send()
    def DIGroup(self, values: str) -> DobotResponse:
        pass

    @send()
    def ToolDI(self, index: int) -> DobotResponse:
        pass

    @send()
    def AI(self, index: int) -> DobotResponse:
        pass

    @send()
    def ToolAI(self, index: int) -> DobotResponse:
        pass

    @send()
    def SetTool485(self, baud: int, parity: str = 'N', stopbit: int = 1, identify: int = None) -> DobotResponse:
        pass

    @send()
    def SetToolPower(self, status: int, identify: int = None) -> DobotResponse:
        pass

    @send()
    def SetToolMode(self, mode: int, type: int, identify: int = None) -> DobotResponse:
        pass

    # endregion
    # -------------
    # region modbus

    @send()
    def ModbusCreate(self, ip: str, port: int, slave_id: int, isRTU: int = None) -> DobotResponse:
        pass

    @send()
    def ModbusRTUCreate(
        self, slave_id: int, baud: int, parity: str = 'E', data_bit: int = 8, stop_bit: int = 1
    ) -> DobotResponse:
        pass

    @send()
    def ModbusClose(self, index: int) -> DobotResponse:
        pass

    @send()
    def GetInBits(self, index: int, address: int, count: int) -> DobotResponse:
        pass

    @send()
    def GetInRegs(self, index: int, address: int, count: int, valType: str = 'U16') -> DobotResponse:
        pass

    @send()
    def GetCoils(self, index: int, address: int, count: int) -> DobotResponse:
        pass

    @send()
    def SetCoils(self, index: int, address: int, count: int, valTab: str) -> DobotResponse:
        pass

    @send()
    def GetHoldRegs(self, index: int, address: int, count: int, valType: str = 'U16') -> DobotResponse:
        pass

    @send()
    def setHoldRegs(self, index: int, address: int, count: int, valTab: str, valType: str = 'U16') -> DobotResponse:
        pass

    # endregion
    # ---------------
    # region register

    @send()
    def GetInputBool(self, adress: int) -> DobotResponse:
        pass

    @send()
    def GetInputInt(self, adress: int) -> DobotResponse:
        pass

    @send()
    def GetInputFloat(self, adress: int) -> DobotResponse:
        pass

    @send()
    def GetOutputBool(self, adress: int) -> DobotResponse:
        pass

    @send()
    def GetOutputInt(self, adress: int) -> DobotResponse:
        pass

    @send()
    def GetOutputFloat(self, adress: int) -> DobotResponse:
        pass

    @send()
    def SetOutputBool(self, adress: int, value: int) -> DobotResponse:
        pass

    @send()
    def SetOutputInt(self, adress: int, value: int) -> DobotResponse:
        pass

    @send()
    def SetOutputFloat(self, adress: int, value: float) -> DobotResponse:
        pass

    # endregion
    # ---------------
    # region movement

    @send()
    def MovJ(
        self,
        P: str,
        _user: int = None,
        _tool: int = None,
        _a: int = None,
        _v: int = None,
        _cp: int = None,
    ) -> DobotResponse:
        pass

    @send()
    def MovL(
        self,
        P: str,
        _user: int = None,
        _tool: int = None,
        _a: int = None,
        _v: int = None,
        _speed: str = None,
        _cp: int = None,
        _r: str = None,
    ) -> DobotResponse:
        pass

    @send()
    def MovLIO(
        self,
        P: str,
        io: str,
        _user: int = None,
        _tool: int = None,
        _a: int = None,
        _v: int = None,
        _speed: int = None,
        _cp: int = None,
        _r: int = None,
    ) -> DobotResponse:
        pass

    @send()
    def MovJIO(
        self,
        P: str,
        io: str,
        _user: int = None,
        _tool: int = None,
        _a: int = None,
        _v: int = None,
        _cp: int = None,
    ) -> DobotResponse:
        pass

    @send()
    def Arc(
        self,
        P1: str,
        P2: str,
        _user: int = None,
        _tool: int = None,
        _a: int = None,
        _v: int = None,
        _speed: int = None,
        _cp: int = None,
        _r: int = None,
        ori_mode: int = None,
    ) -> DobotResponse:
        pass

    @send()
    def Circle(
        self,
        P1: str,
        P2: str,
        count: int,
        _user: int = None,
        _tool: int = None,
        _a: int = None,
        _v: int = None,
        _speed: int = None,
        _cp: int = None,
        _r: int = None,
    ) -> DobotResponse:
        pass

    @send()
    def ServoJ(
        self,
        J1: float,
        J2: float,
        J3: float,
        J4: float,
        J5: float,
        J6: float,
        t: float = 0.1,
        aheadtime: float = 50,
        gain: float = 500,
    ) -> DobotResponse:
        pass

    @send()
    def ServoP(
        self,
        X: float,
        Y: float,
        Z: float,
        Rx: float,
        Ry: float,
        Rz: float,
        t: float = 0.1,
        aheadtime: float = 50,
        gain: float = 500,
    ) -> DobotResponse:
        pass

    @send()
    def MoveJog(self, axisID: str = None, _coordType: int = 0, _user: int = 0, _tool: int = 0) -> DobotResponse:
        pass

    @send()
    def RunTo(
        self,
        P: str,
        moveType: int,
        _user: int = None,
        _tool: int = None,
        _a: int = None,
        _v: int = None,
    ) -> DobotResponse:
        pass

    @send()
    def GetStartPose(self, traceName: str) -> DobotResponse:
        pass

    @send()
    def StartPath(
        self,
        traceName: str,
        isConst: int,
        multi: float,
        _sample: int = 50,
        _freq: float = 0.2,
        _user: int = 0,
        _tool: int = 0,
    ) -> DobotResponse:
        pass

    @send()
    def RelMovJTool(
        self,
        offsetX: float,
        offsetY: float,
        offsetZ: float,
        offsetRx: float,
        offsetRy: float,
        offsetRz: float,
        _user: int = None,
        _tool: int = None,
        _a: int = None,
        _v: int = None,
        _cp: int = None,
    ) -> DobotResponse:
        pass

    @send()
    def RelMovLTool(
        self,
        offsetX: float,
        offsetY: float,
        offsetZ: float,
        offsetRx: float,
        offsetRy: float,
        offsetRz: float,
        _user: int = None,
        _tool: int = None,
        _a: int = None,
        _v: int = None,
        _speed: int = None,
        _cp: int = None,
        _r: int = None,
    ) -> DobotResponse:
        pass

    @send()
    def RelMovJUser(
        self,
        offsetX: float,
        offsetY: float,
        offsetZ: float,
        offsetRx: float,
        offsetRy: float,
        offsetRz: float,
        _user: int = None,
        _tool: int = None,
        _a: int = None,
        _v: int = None,
        _cp: int = None,
    ) -> DobotResponse:
        pass

    @send()
    def RelMovLUser(
        self,
        offsetX: float,
        offsetY: float,
        offsetZ: float,
        offsetRx: float,
        offsetRy: float,
        offsetRz: float,
        _user: int = None,
        _tool: int = None,
        _a: int = None,
        _v: int = None,
        _speed: int = None,
        _cp: int = None,
        _r: int = None,
    ) -> DobotResponse:
        pass

    @send()
    def RelJointMovJ(
        self,
        offset1: float,
        offset2: float,
        offset3: float,
        offset4: float,
        offset5: float,
        offset6: float,
        _user: int = None,
        _tool: int = None,
        _a: int = None,
        _v: int = None,
        _cp: int = None,
    ) -> DobotResponse:
        pass

    @send()
    def RelPointTool(self, P: str, offset: str) -> DobotResponse:
        pass

    @send()
    def RelPointUser(self, P: str, offset: str) -> DobotResponse:
        pass

    @send()
    def RelJoint(self, J1: float, J2: float, J3: float, J4: float, J5: float, J6: float, offset: str) -> DobotResponse:
        pass

    @send()
    def GetCurrentCommandID(self) -> DobotResponse:
        pass

    # endregion
    # -----------
    # region recovery

    @send()
    def SetResumeOffset(self, distance: float) -> DobotResponse:
        pass

    @send()
    def PathRecovery(self) -> DobotResponse:
        pass

    @send()
    def PathRecoveryStop(self) -> DobotResponse:
        pass

    @send()
    def PathRecoveryStatus(self) -> DobotResponse:
        pass

    # endregion
    # -----------------
    # region log export

    @send()
    def LogExportUSB(self, range: int) -> DobotResponse:
        pass

    @send()
    def GetExportStatus(self) -> DobotResponse:
        pass

    # endregion
    # ------------
    # region force

    @send()
    def EnableFTSensor(self, status: int) -> DobotResponse:
        pass

    @send()
    def SixForceHome(self) -> DobotResponse:
        pass

    @send()
    def GetForce(self, tool: int = 0) -> DobotResponse:
        pass

    @send()
    def ForceDriveMode(self, control: str, _user: int = 0) -> DobotResponse:
        pass

    @send()
    def ForceDriveSpped(self, speed: int) -> DobotResponse:
        pass

    @send()
    def FCForceMode(
        self, control: str, force: str, _reference: int = 0, _user: int = 0, _tool: int = 0
    ) -> DobotResponse:
        pass

    @send()
    def FCSetDeviation(self, deviation: str, controltype: int = 0) -> DobotResponse:
        pass

    @send()
    def FCSetForceLimit(
        self, x: float = 500, y: float = 500, z: float = 500, rx: float = 50, ry: float = 50, rz: float = 50
    ) -> DobotResponse:
        pass

    @send()
    def FCSetMass(
        self, x: float = 20, y: float = 20, z: float = 20, rx: float = 0.5, ry: float = 0.5, rz: float = 0.5
    ) -> DobotResponse:
        pass

    @send()
    def FCSetDamping(
        self, x: float = 50, y: float = 50, z: float = 50, rx: float = 20, ry: float = 20, rz: float = 20
    ) -> DobotResponse:
        pass

    @send()
    def FCOff(self) -> DobotResponse:
        pass

    @send()
    def FCSetForceSpeedLimit(
        self, x: float = 20, y: float = 20, z: float = 20, rx: float = 20, ry: float = 20, rz: float = 20
    ) -> DobotResponse:
        pass

    @send()
    def FCSetForce(self, x: float, y: float, z: float, rx: float, ry: float, rz: float) -> DobotResponse:
        pass

    # endregion


if __name__ == '__main__':
    dobot = Dobot()
    dobot.enableDebug = True
