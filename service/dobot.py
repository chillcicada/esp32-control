"""
Dobot TCP Wrapper Based on Function Signatures

@author: chillcicada
@license: MIT
"""
from typing import List, Any
from functools import wraps
from inspect import signature

# region uart
# import .uart
from maix import pinmap, uart

pinmap.set_pin_function('A29', 'UART2_RX')
pinmap.set_pin_function('A28', 'UART2_TX')
serial_esp = uart.UART('/dev/ttyS2', 115200)

# endregion

# region conn
# from .conn import SerialConn, SocketConn
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

    def recv(self, buffer_size: int) -> str:
        if self.conn:
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

    def recv(self, buffer_size: int) -> str:
        if self.conn and self.conn.is_open:
            return self.conn.read(buffer_size).decode()
        return ''

    def settimeout(self, timeout: float) -> None:
        if self.conn and self.conn.is_open:
            self.conn.timeout = timeout
# endregion

# Use type aliases for better readability
DobotResponse = List[Any]
DobotResponse2 = List[Any]


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
    REQ_PARAM_OVER_RANGE = -40000  # -4000X
    OPT_PARAM_TYPE_ERROR = -50000  # -5000X
    OPT_PARAM_OVER_RANGE = -60000  # -6000X


class Dobot:
    def __init__(self, address, isSerial: bool = False):
        self.address = address
        self.conn = SerialConn() if isSerial else SocketConn()
        self.isDebug = False

    # core functions used to communicate with Dobot
    # region core

    def handle(self, err: int, params: list, cmd: str) -> DobotResponse:
        if err == DobotErrorCode.SUCCESS:
            return params

        if err < DobotErrorCode.OPT_PARAM_OVER_RANGE:
            self.error(f'Optional parameter at {DobotErrorCode.OPT_PARAM_OVER_RANGE - err} in {cmd} out of range.')
        elif err < DobotErrorCode.OPT_PARAM_TYPE_ERROR:
            self.error(f'Optional parameter at {DobotErrorCode.OPT_PARAM_TYPE_ERROR - err} in {cmd} type error.')
        elif err < DobotErrorCode.REQ_PARAM_OVER_RANGE:
            self.error(f'Required parameter at {DobotErrorCode.REQ_PARAM_OVER_RANGE - err} in {cmd} out of range.')
        elif err < DobotErrorCode.REQ_PARAM_TYPE_ERROR:
            self.error(f'Required parameter at {DobotErrorCode.REQ_PARAM_TYPE_ERROR - err} in {cmd} type error.')

        match err:
            case DobotErrorCode.EXECUTION_FAILED:
                self.error('Execution failed.')
            case DobotErrorCode.ALARMED:
                self.error('Robot is in alarmed state.')
                self.ClearError()
                time.sleep(1)
            case DobotErrorCode.EMERGENCY_STOP:
                self.error('Emergency stop activated.')
            case DobotErrorCode.POWER_OFF:
                self.error('Power is off.')
            case DobotErrorCode.SCRIPT_RUNNING:
                self.error('Script is running.')
            case DobotErrorCode.MISMATCHED:
                self.error(f'Mismatched move command {cmd} with type.')
            case DobotErrorCode.SCRIPT_PAUSED:
                self.error('Script is paused.')
            case DobotErrorCode.AUTH_EXPIRED:
                self.error('Authorization expired.')
            case DobotErrorCode.CMD_NOT_FOUND:
                self.error(f'Command {cmd} not found.')
            case DobotErrorCode.PARAM_NUM_ERROR:
                self.error(f'Parameter number error in command {cmd}.')
            case _:
                self.error(f'Unknown error code: {err}')

        return params

    def parse(self, response: str, cmd: str, handler=None) -> DobotResponse:
        parts = response.split(',', 1)
        assert len(parts) == 2, 'Invalid response format.'

        err, params = parts
        err = int(err)
        params = params[1:-1]  # remove the surrounding braces
        params = [float(p) if '.' in p else int(p) for p in params.split(',')] if params else []

        self.debug(f'Parsed error code: {err}, params: {params}')

        return handler(err, params, cmd) if handler else self.handle(err, params, cmd)

    def send_cmd(self, cmd: str, handler=None) -> DobotResponse:
        if not self.conn.status:
            self.error('Not connected to Dobot.')
            raise ConnectionError('Not connected to Dobot.')
        
        self.conn.send(cmd.encode())
        self.debug(f'Sent command: {cmd}')

        response = self.conn.recv(400).strip()
        self.debug(f'Response: {response}')
        return self.parse(response.removesuffix(f',{cmd};'), cmd, handler)

    @staticmethod
    def send(handler=None):
        def decorator(func):
            @wraps(func)
            def sender(self: 'Dobot', *args, **kwargs) -> DobotResponse:
                sign = signature(func)
                func_name = func.__name__
                return_type = sign.return_annotation

                if return_type == DobotResponse:
                    bound = sign.bind(self, *args, **kwargs)
                    bound.apply_defaults()
                    params = [
                        f'{k.removeprefix("_")}={v}' if k.startswith('_') else str(v)
                        for k, v in bound.arguments.items()
                        if k != 'self' and v is not None
                    ]
                    cmd = f'{func_name}({",".join(params)})'
                elif return_type == DobotResponse2:
                    params = func(self, *args, **kwargs)
                    cmd = params
                else:
                    self.error(f'Invalid return type for {func_name}: {return_type}')
                    raise TypeError(f'Invalid return type for {func_name}: {return_type}')

                return self.send_cmd(cmd)

            return sender

        return decorator

    def debug(self, str: str) -> None:
        if self.isDebug:
            print(f'[Dobot DEBUG] {str}')

    def error(self, str: str) -> None:
        print(f'[Dobot ERROR] {str}')

    def connect(self, timeout=None) -> None:
        try:
            self.debug(f'Connecting to {self.address}')
            self.conn.connect(self.address)
            self.conn.settimeout(timeout)
            self.debug('Connection established.')

        except Exception as e:
            self.error(f'Connection failed: {e}')
            self.conn = None

    def disconnect(self) -> None:
        if not self.conn.status:
            self.debug('No active connection to disconnect.')
            return

        self.debug('Disconnecting...')
        self.conn.disconnect()
        self.conn = None
        self.debug('Disconnected.')

    def enable_debug(self) -> None:
        self.isDebug = True

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
    # ---------------
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
    # -------------
    # region export

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
    # self-defined functions for easier usage can be added below
    # ------------
    # region extra

    def Grab(self, close: bool, length=None) -> DobotResponse:
        return self.send_cmd(f'SetParallelGripper({length or 38 if close else 70})')

    def MovJJoint(
        self,
        jointList: list,
        user: int = None,
        tool: int = None,
        a: int = None,
        v: int = None,
        cp: int = None,
    ) -> DobotResponse:
        assert len(jointList) == 6, 'jointList must contain exactly 6 elements.'
        return self.MovJ(f'joint={{{",".join(map(str, jointList))}}}', user, tool, a, v, cp)

    def MovJPose(
        self,
        poseList: list,
        user: int = None,
        tool: int = None,
        a: int = None,
        v: int = None,
        cp: int = None,
    ) -> DobotResponse:
        assert len(poseList) == 6, 'poseList must contain exactly 6 elements.'
        return self.MovJ(f'pose={{{",".join(map(str, poseList))}}}', user, tool, a, v, cp)

    def MovLJoint(
        self,
        jointList: list,
        user: int = None,
        tool: int = None,
        a: int = None,
        v: int = None,
        speed: str = None,
        cp: int = None,
        r: str = None,
    ) -> DobotResponse:
        assert len(jointList) == 6, 'jointList must contain exactly 6 elements.'
        return self.MovL(f'joint={{{",".join(map(str, jointList))}}}', user, tool, a, v, speed, cp, r)

    def MovLPose(
        self,
        poseList: list,
        user: int = None,
        tool: int = None,
        a: int = None,
        v: int = None,
        speed: str = None,
        cp: int = None,
        r: str = None,
    ) -> DobotResponse:
        assert len(poseList) == 6, 'poseList must contain exactly 6 elements.'
        return self.MovL(f'pose={{{",".join(map(str, poseList))}}}', user, tool, a, v, speed, cp, r)

    def RelPointUserJoint(
        self,
        jointList: list,
        offsetList: list,
    ) -> DobotResponse:
        assert len(jointList) == 6, 'jointList must contain exactly 6 elements.'
        assert len(offsetList) == 6, 'offsetList must contain exactly 6 elements.'
        return self.RelPointUser(f'joint={{{",".join(map(str, jointList))}}}', f'{{{",".join(map(str, offsetList))}}}')

    def RelPointUserPose(
        self,
        poseList: list,
        offsetList: list,
    ) -> DobotResponse:
        assert len(poseList) == 6, 'poseList must contain exactly 6 elements.'
        assert len(offsetList) == 6, 'offsetList must contain exactly 6 elements.'
        return self.RelPointUser(f'pose={{{",".join(map(str, poseList))}}}', f'{{{",".join(map(str, offsetList))}}}')

    def Home(self) -> DobotResponse:
        return self.MovJJoint([0, 0, 0, 0, 0, 0])

    def Pack(self) -> DobotResponse:
        return self.MovJJoint([-90, 0, -140, -40, 0, 0])

    def Stay(self) -> DobotResponse:
        return self.MovJJoint([0, 0, 90, 0, 90, 0])

    # endregion


if __name__ == '__main__':
    import time

    P1 = [-180, -20, -110, -50, -60, 0]
    P2 = [-120, -20, -110, -50, -30, 0]
    P3 = [-150, -30, -100, -50, -60, 0]
    P4 = [-100, -30, -100, -50, -50, 0]

    dobot = Dobot('/dev/ttyS0', isSerial=True)

    dobot.enable_debug()

    dobot.connect(5)

    # dobot.ClearError()

    # time.sleep(2)

    dobot.EnableRobot(0.2, 0, 0, 0, 1)

    time.sleep(1)

    dobot.Pack()

    # dobot.Grab(False)

    # time.sleep(1)

    # dobot.MovJJoint(P2)

    # time.sleep(1)

    # pose = dobot.RelPointUserJoint(P2, [0, 0, -30, 0, 0, 0])

    # dobot.MovLPose(pose)

    # time.sleep(1)

    # dobot.Grab(True)

    # time.sleep(1)

    # dobot.MovJJoint(P1)

    # pose = dobot.RelPointUserJoint(P1, [0, 0, 160, 0, 0, 0])

    # dobot.MovLPose(pose)

    # time.sleep(2)

    # serial_esp.write(b'MIX\n')

    time.sleep(2)

    dobot.DisableRobot()

    dobot.disconnect()
