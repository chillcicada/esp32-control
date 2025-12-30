from functools import wraps
from inspect import signature

from conn import SerialConn, SocketConn


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
    def __init__(self, address, isSerial: bool = False, name='Dobot', handle=print):
        self.address = address
        self.name = name
        self.conn = SerialConn(name) if isSerial else SocketConn()
        self.handle = handle
        self.isDebug = False

    # core functions used to communicate with Dobot
    # region core

    def resolve(self, err: int, params: list, cmd: str):
        if err == DobotErrorCode.SUCCESS:
            self.debug(f'Get Params: {params}')
            return params

        self.debug(f'Error Code {err} with `{cmd}`')

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
                self.error('Emergency stop activated, disconnect')
                self.disconnect()
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

    def parse(self, res: str, cmd: str, resolver=None):
        func_name, _ = cmd.split('(', 1)
        err, params_ = res.split(',{', 1)
        params, _ = params_.split('},' + func_name, 1)

        err = int(err)
        # params = params[1:-1]
        params = [float(p) if '.' in p else int(p) for p in params.split(',')] if params else []
        cmd = func_name + _

        return resolver(err, params, cmd) if resolver else self.resolve(err, params, cmd)

    def send_cmd(self, cmd: str, handler=None):
        if not (self.conn and self.conn.status):
            self.error('Not connected to Dobot.')
            raise ConnectionError('Not connected to Dobot.')

        self.conn.send(cmd)

        res = self.conn.recv()

        if res == 'Control Mode Is Not Tcp':
            self.disconnect()
            raise ConnectionError('Control mode is online mode instead of tcp mode, disconnect')

        try:
            assert res.endswith(';'), 'Invalid response format from Dobot.'
            return self.parse(res.removesuffix(';'), cmd, handler)

        except Exception as e:
            self.error(f'Error parsing response: {e}')
            return []

    @staticmethod
    def send(resolver=None):
        def decorator(func):
            @wraps(func)
            def sender(self: 'Dobot', *args, **kwargs):
                sign = signature(func)
                func_name = func.__name__

                bound = sign.bind(self, *args, **kwargs)
                bound.apply_defaults()
                params = [
                    f'{k.removeprefix("_")}={v}' if k.startswith('_') else str(v)
                    for k, v in bound.arguments.items()
                    if k != 'self' and v is not None
                ]
                cmd = f'{func_name}({",".join(params)})'

                return self.send_cmd(cmd, resolver)

            return sender

        return decorator

    def info(self, msg: str, supply='') -> None:
        supply = f'{supply or self.name}'
        self.handle(f'-- [I] [{supply:^18}] {msg}')

    def debug(self, msg: str, supply='') -> None:
        if self.isDebug:
            supply = f'{supply or self.name}'
            self.handle(f'-- [D] [{supply:^18}] {msg}')

    def warning(self, msg: str, supply='') -> None:
        supply = f'{supply or self.name}'
        self.handle(f'-- [W] [{supply:^18}] {msg}')

    def error(self, msg: str, supply='') -> None:
        supply = f'{supply or self.name}'
        self.handle(f'-- [E] [{supply:^18}] {msg}')

    def connect(self) -> None:
        if not self.conn:
            raise ConnectionError('Conn is not prepared!')

        try:
            self.info(f'Connecting to {self.address}')
            self.conn.connect(self.address)
            self.info('Connection established.')

        except Exception as e:
            self.error(f'Connection failed: {e}')
            self.conn = None

    def disconnect(self) -> None:
        if not (self.conn and self.conn.status):
            self.debug('No active connection to disconnect.')
            return

        self.info('Disconnecting...')
        self.conn.disconnect()
        self.conn = None
        self.info('Disconnected.')

    def enable_debug(self) -> None:
        self.isDebug = True

    # endregion
    # --------------
    # region control

    @send()
    def RequestControl(self):
        pass

    @send()
    def PowerON(self):
        pass

    @send()
    def EnableRobot(
        self,
        load: float | None = None,
        centerX: float | None = None,
        centerY: float | None = None,
        centerZ: float | None = None,
        isCheck: int | None = None,
    ):
        pass

    @send()
    def DisableRobot(self):
        pass

    @send()
    def ClearError(self):
        pass

    @send()
    def RunScript(self, projectName: str):
        pass

    @send()
    def Stop(self):
        pass

    @send()
    def Pause(self):
        pass

    @send()
    def Continue(self):
        pass

    @send()
    def EmergencyStop(self, mode: str):
        pass

    @send()
    def BrakeControl(self, axisID: int, value: int):
        pass

    @send()
    def StartDrag(self):
        pass

    @send()
    def StopDrag(self):
        pass

    # endregion
    # ---------------
    # region settings

    @send()
    def SpeedFactor(self, ratio: int = 0):
        pass

    @send()
    def User(self, index: int):
        pass

    @send()
    def SetUser(self, index: int, value: str, type: int = 0):
        pass

    @send()
    def CalcUser(self, index: int, matrix: int, offset: int):
        pass

    @send()
    def Tool(self, index: int = 0):
        pass

    @send()
    def SetTool(self, index: int, value: str, type: int = 0):
        pass

    @send()
    def CalcTool(self, index: int, matrix: int, offset: str):
        pass

    @send()
    def SetPayload(
        self, load_or_name: str | float, x: float | None = None, y: float | None = None, z: float | None = None
    ):
        pass

    @send()
    def AccJ(self, R: int = 100):
        pass

    @send()
    def AccL(self, R: int = 100):
        pass

    @send()
    def VelJ(self, R: int = 100):
        pass

    @send()
    def VelL(self, R: int = 100):
        pass

    @send()
    def CP(self, R: int = 0):
        pass

    @send()
    def SetCollisionLevel(self, level: int):
        pass

    @send()
    def SetBackDistance(self, distance: float):
        pass

    @send()
    def SetPostCollisionMode(self, mode: int):
        pass

    @send()
    def DragSensitivity(self, index: int, value: int):
        pass

    @send()
    def EnableSafeSkin(self, status: int):
        pass

    @send()
    def SetSafeSkin(self, part: int, status: int):
        pass

    @send()
    def SetSafeWallEnable(self, index: int, value: int):
        pass

    @send()
    def SetWorkZoneEnable(self, index: int, value: int):
        pass

    # endregion
    # ------------------
    # region calculation

    @send()
    def RobotMode(self):
        pass

    @send()
    def PositiveKin(
        self, J1: float, J2: float, J3: float, J4: float, J5: float, J6: float, _user: int = 0, _tool: int = 0
    ):
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
    ):
        pass

    @send()
    def GetAngle(self):
        pass

    @send()
    def GetPose(self, _user: int = 0, _tool: int = 0):
        pass

    @send()
    def GetErrorID(self):
        pass

    @send()
    def Create1DTray(self, Trayname: str, Count: str, Points: str):
        pass

    @send()
    def Create2DTray(self, Trayname: str, Count: str, Points: str):
        pass

    @send()
    def Create3DTray(self, Trayname: str, Count: str, Points: str):
        pass

    @send()
    def GetTrayPoint(self, Trayname: str, index: int):
        pass

    # endregion
    # ---------
    # region io

    @send()
    def DO(self, index: int, status: int, time: int | None = None):
        pass

    @send()
    def DOInstant(self, index: int, status: int):
        pass

    @send()
    def GetDO(self, index: int):
        pass

    @send()
    def DOGroup(self, values: str):
        pass

    @send()
    def GetDOGroup(self, values: str):
        pass

    @send()
    def ToolDO(self, index: int, status: int):
        pass

    @send()
    def ToolDOInstant(self, index: int, status: int):
        pass

    @send()
    def GetToolDO(self, index: int):
        pass

    @send()
    def AO(self, index: int, value: int):
        pass

    @send()
    def AOInstant(self, index: int, value: int):
        pass

    @send()
    def GetAO(self, index: int):
        pass

    @send()
    def DI(self, index: int):
        pass

    @send()
    def DIGroup(self, values: str):
        pass

    @send()
    def ToolDI(self, index: int):
        pass

    @send()
    def AI(self, index: int):
        pass

    @send()
    def ToolAI(self, index: int):
        pass

    @send()
    def SetTool485(self, baud: int, parity: str = 'N', stopbit: int = 1, identify: int | None = None):
        pass

    @send()
    def SetToolPower(self, status: int, identify: int | None = None):
        pass

    @send()
    def SetToolMode(self, mode: int, type: int, identify: int | None = None):
        pass

    # endregion
    # -------------
    # region modbus

    @send()
    def ModbusCreate(self, ip: str, port: int, slave_id: int, isRTU: int | None = None):
        pass

    @send()
    def ModbusRTUCreate(self, slave_id: int, baud: int, parity: str = 'E', data_bit: int = 8, stop_bit: int = 1):
        pass

    @send()
    def ModbusClose(self, index: int):
        pass

    @send()
    def GetInBits(self, index: int, address: int, count: int):
        pass

    @send()
    def GetInRegs(self, index: int, address: int, count: int, valType: str = 'U16'):
        pass

    @send()
    def GetCoils(self, index: int, address: int, count: int):
        pass

    @send()
    def SetCoils(self, index: int, address: int, count: int, valTab: str):
        pass

    @send()
    def GetHoldRegs(self, index: int, address: int, count: int, valType: str = 'U16'):
        pass

    @send()
    def setHoldRegs(self, index: int, address: int, count: int, valTab: str, valType: str = 'U16'):
        pass

    # endregion
    # ---------------
    # region register

    @send()
    def GetInputBool(self, adress: int):
        pass

    @send()
    def GetInputInt(self, adress: int):
        pass

    @send()
    def GetInputFloat(self, adress: int):
        pass

    @send()
    def GetOutputBool(self, adress: int):
        pass

    @send()
    def GetOutputInt(self, adress: int):
        pass

    @send()
    def GetOutputFloat(self, adress: int):
        pass

    @send()
    def SetOutputBool(self, adress: int, value: int):
        pass

    @send()
    def SetOutputInt(self, adress: int, value: int):
        pass

    @send()
    def SetOutputFloat(self, adress: int, value: float):
        pass

    # endregion
    # ---------------
    # region movement

    @send()
    def MovJ(
        self,
        P: str,
        _user: int | None = None,
        _tool: int | None = None,
        _a: int | None = None,
        _v: int | None = None,
        _cp: int | None = None,
    ):
        pass

    @send()
    def MovL(
        self,
        P: str,
        _user: int | None = None,
        _tool: int | None = None,
        _a: int | None = None,
        _v: int | None = None,
        _speed: str | None = None,
        _cp: int | None = None,
        _r: str | None = None,
    ):
        pass

    @send()
    def MovLIO(
        self,
        P: str,
        io: str,
        _user: int | None = None,
        _tool: int | None = None,
        _a: int | None = None,
        _v: int | None = None,
        _speed: int | None = None,
        _cp: int | None = None,
        _r: int | None = None,
    ):
        pass

    @send()
    def MovJIO(
        self,
        P: str,
        io: str,
        _user: int | None = None,
        _tool: int | None = None,
        _a: int | None = None,
        _v: int | None = None,
        _cp: int | None = None,
    ):
        pass

    @send()
    def Arc(
        self,
        P1: str,
        P2: str,
        _user: int | None = None,
        _tool: int | None = None,
        _a: int | None = None,
        _v: int | None = None,
        _speed: int | None = None,
        _cp: int | None = None,
        _r: int | None = None,
        ori_mode: int | None = None,
    ):
        pass

    @send()
    def Circle(
        self,
        P1: str,
        P2: str,
        count: int,
        _user: int | None = None,
        _tool: int | None = None,
        _a: int | None = None,
        _v: int | None = None,
        _speed: int | None = None,
        _cp: int | None = None,
        _r: int | None = None,
    ):
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
    ):
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
    ):
        pass

    @send()
    def MoveJog(self, axisID: str | None = None, _coordType: int = 0, _user: int = 0, _tool: int = 0):
        pass

    @send()
    def RunTo(
        self,
        P: str,
        moveType: int,
        _user: int | None = None,
        _tool: int | None = None,
        _a: int | None = None,
        _v: int | None = None,
    ):
        pass

    @send()
    def GetStartPose(self, traceName: str):
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
    ):
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
        _user: int | None = None,
        _tool: int | None = None,
        _a: int | None = None,
        _v: int | None = None,
        _cp: int | None = None,
    ):
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
        _user: int | None = None,
        _tool: int | None = None,
        _a: int | None = None,
        _v: int | None = None,
        _speed: int | None = None,
        _cp: int | None = None,
        _r: int | None = None,
    ):
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
        _user: int | None = None,
        _tool: int | None = None,
        _a: int | None = None,
        _v: int | None = None,
        _cp: int | None = None,
    ):
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
        _user: int | None = None,
        _tool: int | None = None,
        _a: int | None = None,
        _v: int | None = None,
        _speed: int | None = None,
        _cp: int | None = None,
        _r: int | None = None,
    ):
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
        _user: int | None = None,
        _tool: int | None = None,
        _a: int | None = None,
        _v: int | None = None,
        _cp: int | None = None,
    ):
        pass

    @send()
    def RelPointTool(self, P: str, offset: str):
        pass

    @send()
    def RelPointUser(self, P: str, offset: str):
        pass

    @send()
    def RelJoint(self, J1: float, J2: float, J3: float, J4: float, J5: float, J6: float, offset: str):
        pass

    @send()
    def GetCurrentCommandID(self):
        pass

    # endregion
    # ---------------
    # region recovery

    @send()
    def SetResumeOffset(self, distance: float):
        pass

    @send()
    def PathRecovery(self):
        pass

    @send()
    def PathRecoveryStop(self):
        pass

    @send()
    def PathRecoveryStatus(self):
        pass

    # endregion
    # -------------
    # region export

    @send()
    def LogExportUSB(self, range: int):
        pass

    @send()
    def GetExportStatus(self):
        pass

    # endregion
    # ------------
    # region force

    @send()
    def EnableFTSensor(self, status: int):
        pass

    @send()
    def SixForceHome(self):
        pass

    @send()
    def GetForce(self, tool: int = 0):
        pass

    @send()
    def ForceDriveMode(self, control: str, _user: int = 0):
        pass

    @send()
    def ForceDriveSpped(self, speed: int):
        pass

    @send()
    def FCForceMode(self, control: str, force: str, _reference: int = 0, _user: int = 0, _tool: int = 0):
        pass

    @send()
    def FCSetDeviation(self, deviation: str, controltype: int = 0):
        pass

    @send()
    def FCSetForceLimit(
        self, x: float = 500, y: float = 500, z: float = 500, rx: float = 50, ry: float = 50, rz: float = 50
    ):
        pass

    @send()
    def FCSetMass(self, x: float = 20, y: float = 20, z: float = 20, rx: float = 0.5, ry: float = 0.5, rz: float = 0.5):
        pass

    @send()
    def FCSetDamping(self, x: float = 50, y: float = 50, z: float = 50, rx: float = 20, ry: float = 20, rz: float = 20):
        pass

    @send()
    def FCOff(self):
        pass

    @send()
    def FCSetForceSpeedLimit(
        self, x: float = 20, y: float = 20, z: float = 20, rx: float = 20, ry: float = 20, rz: float = 20
    ):
        pass

    @send()
    def FCSetForce(self, x: float, y: float, z: float, rx: float, ry: float, rz: float):
        pass

    # endregion
    # ------------
    # self-defined functions for easier usage can be added below
    # region extra

    def Grab(self, close: bool, length=None):
        return self.send_cmd(f'SetParallelGripper({length or 38 if close else 70})')

    def MovJJoint(
        self,
        jointList: list,
        user: int | None = None,
        tool: int | None = None,
        a: int | None = None,
        v: int | None = None,
        cp: int | None = None,
    ):
        assert len(jointList) == 6, 'jointList must contain exactly 6 elements.'
        return self.MovJ(f'joint={{{",".join(map(str, jointList))}}}', user, tool, a, v, cp)

    def MovJPose(
        self,
        poseList: list,
        user: int | None = None,
        tool: int | None = None,
        a: int | None = None,
        v: int | None = None,
        cp: int | None = None,
    ):
        assert len(poseList) == 6, 'poseList must contain exactly 6 elements.'
        return self.MovJ(f'pose={{{",".join(map(str, poseList))}}}', user, tool, a, v, cp)

    def MovLJoint(
        self,
        jointList: list,
        user: int | None = None,
        tool: int | None = None,
        a: int | None = None,
        v: int | None = None,
        speed: str | None = None,
        cp: int | None = None,
        r: str | None = None,
    ):
        assert len(jointList) == 6, 'jointList must contain exactly 6 elements.'
        return self.MovL(f'joint={{{",".join(map(str, jointList))}}}', user, tool, a, v, speed, cp, r)

    def MovLPose(
        self,
        poseList: list,
        user: int | None = None,
        tool: int | None = None,
        a: int | None = None,
        v: int | None = None,
        speed: str | None = None,
        cp: int | None = None,
        r: str | None = None,
    ):
        assert len(poseList) == 6, 'poseList must contain exactly 6 elements.'
        return self.MovL(f'pose={{{",".join(map(str, poseList))}}}', user, tool, a, v, speed, cp, r)

    def RelPointUserJoint(
        self,
        jointList: list,
        offsetList: list,
    ):
        assert len(jointList) == 6, 'jointList must contain exactly 6 elements.'
        assert len(offsetList) == 6, 'offsetList must contain exactly 6 elements.'
        return self.RelPointUser(f'joint={{{",".join(map(str, jointList))}}}', f'{{{",".join(map(str, offsetList))}}}')

    def RelPointUserPose(
        self,
        poseList: list,
        offsetList: list,
    ):
        assert len(poseList) == 6, 'poseList must contain exactly 6 elements.'
        assert len(offsetList) == 6, 'offsetList must contain exactly 6 elements.'
        return self.RelPointUser(f'pose={{{",".join(map(str, poseList))}}}', f'{{{",".join(map(str, offsetList))}}}')

    def Home(self):
        return self.MovJJoint([0, 0, 0, 0, 0, 0])

    def Pack(self):
        return self.MovJJoint([-90, 0, -140, -40, 0, 0])

    def Stay(self):
        return self.MovJJoint([0, 0, 90, 0, 90, 0])

    # endregion


if __name__ == '__main__':
    from maix import pinmap, time

    # init UART0 for communication with dobot arm
    dobot = Dobot('/dev/ttyS0', isSerial=True)
    dobot.enable_debug()

    dobot.connect()
    time.sleep(1)

    # init UART2 for communication with embedded ESP32
    pinmap.set_pin_function('A29', 'UART2_RX')
    pinmap.set_pin_function('A28', 'UART2_TX')
    esp = SerialConn('ESP32')
    esp.connect('/dev/ttyS2')

    MAX_STEPS = 0
    STEPPER_UP_RPM = 200
    STEPPER_DOWN_RPM = 40

    INIT_PH = 7.0

    esp.send('START')
    handle = esp.recv()

    if handle == 'READY':
        dobot.info(f'{esp.name} ready', esp.name)
    else:
        dobot.warning(f'Not recv from {esp.name}', esp.name)
        raise ConnectionError('ESP32 is not prepared.')

    # define the positions
    station_1 = [-170, -30, -90, -60, -80, 0]
    station_2 = [-130, -30, -90, -60, -40, 0]

    position_1 = [-160, -30, -80, -70, 20, 0]
    position_2 = [-140, -30, -80, -70, -140, 0]

    # below is a step-by-step example of using the Dobot class
    dobot.ClearError()
    dobot.EnableRobot(0.2, 0, 0, 0, 1)
    time.sleep(1)

    dobot.SpeedFactor(40)
    dobot.Grab(False)

    dobot.MovJJoint(position_2)
    time.sleep(2)

    dobot.RelMovLTool(0, -70, 0, 0, 0, 0)
    time.sleep(2.5)

    dobot.Grab(True)
    dobot.MovLJoint(position_2)
    time.sleep(1)

    dobot.MovJJoint(station_2)
    time.sleep(1)

    dobot.RelMovLTool(0, 150, 0, 0, 0, 0)
    time.sleep(3)

    esp.send('GET_MAX_STEPS')
    data_MAX_STEPS = esp.recv()
    if not data_MAX_STEPS.startswith('MAX_STEPS'):
        dobot.error('Invalid MAX_STEPS response from ESP32.')
    MAX_STEPS = int(data_MAX_STEPS.split(':')[1])
    dobot.info(f'Max steps from {esp.name}: {MAX_STEPS}', esp.name)

    esp.send('DO_INJECT')
    handle = esp.recv()

    if handle == 'STEPPER_START':
        dobot.info('Start', 'Stepper Moter')

        esp.send(f'SET_STEPPER:{STEPPER_UP_RPM},4000,UP')

        while True:
            handle = esp.recv()
            if handle.startswith('STEPPER_CONFIGURED'):
                configured_params = handle.split(':', 1)[1]
                dobot.info(f'Stepper configured: {configured_params}', 'Stepper Moter')
            elif handle == 'STEPPER_CONFIG_INVALID' or handle == 'STEPPER_RECV_INVALID':
                dobot.warning('Stepper configuration invalid', 'Stepper Moter')
            elif handle == 'STEPPER_DONE':
                dobot.info('Done', 'Stepper Moter')
                break
    else:
        dobot.warning(f'Not recv from {esp.name}', esp.name)

    time.sleep(4)

    dobot.MovLJoint(station_2)
    time.sleep(1)

    dobot.MovJJoint(position_2)
    time.sleep(1)

    dobot.RelMovLTool(0, -70, 0, 0, 0, 0, _v=50)
    time.sleep(3)

    dobot.Grab(False)
    dobot.MovLJoint(position_2)
    time.sleep(1)

    dobot.MovJJoint(station_2)
    dobot.MovJJoint(position_1)
    time.sleep(3)

    dobot.RelMovLTool(0, -70, 0, 0, 0, 0)
    time.sleep(3)
    dobot.Grab(True)

    dobot.MovLJoint(position_1)
    time.sleep(1)

    dobot.MovJJoint(station_1)
    time.sleep(1)

    dobot.RelMovLTool(0, 150, 0, 0, 0, 0)
    time.sleep(3)

    esp.send('GET_PH')
    data_PH = esp.recv()
    if not data_PH.startswith('pH'):
        dobot.error('Invalid pH response from ESP32.')
    INIT_PH = float(data_PH.split(':')[1])
    dobot.info(f'Initial pH from {esp.name}: {INIT_PH}', esp.name)
    time.sleep(4)

    dobot.MovLJoint(station_1)
    time.sleep(1)

    _counter = 5
    while _counter <= 5:
        _counter += 1

        # INJECT

        dobot.MovJJoint(station_2)
        time.sleep(1)

        dobot.RelMovLTool(0, 80, 0, 0, 0, 0)
        time.sleep(3)

        esp.send('DO_INJECT')
        handle = esp.recv()

        if handle == 'STEPPER_START':
            dobot.info('Start', 'Stepper Moter')

            esp.send(f'SET_STEPPER:{STEPPER_DOWN_RPM},4000,DOWN')

            while True:
                handle = esp.recv()
                if handle.startswith('STEPPER_CONFIGURED'):
                    configured_params = handle.split(':', 1)[1]
                    dobot.info(f'Stepper configured: {configured_params}', 'Stepper Moter')
                elif handle == 'STEPPER_CONFIG_INVALID' or handle == 'STEPPER_RECV_INVALID':
                    dobot.warning('Stepper configuration invalid', 'Stepper Moter')
                elif handle == 'STEPPER_DONE':
                    dobot.info('Done', 'Stepper Moter')
                    break
        else:
            dobot.warning(f'Not recv from {esp.name}', esp.name)

        time.sleep(4)

        dobot.MovLJoint(station_2)
        time.sleep(1)

        # MIX

        dobot.MovJJoint(station_1)
        time.sleep(1)

        dobot.RelMovLTool(0, 150, 0, 0, 0, 0)
        time.sleep(3)

        esp.send('DO_MIX')
        handle = esp.recv()

        if handle == 'MIX_START':
            dobot.info('mixing start', 'Mixing Moter')
            while True:
                handle = esp.recv()
                time.sleep_us(100)
                if handle == 'MIX_DONE':
                    dobot.info('mixing done', 'Mixing Moter')
                    break
        else:
            dobot.warning(f'Not recv from {esp.name}', esp.name)

        time.sleep(1)

        dobot.MovLJoint(station_1)
        time.sleep(1)

    esp.send('DONE')
    handle = esp.recv()

    if handle == 'DONE':
        dobot.info(f'{esp.name} done', esp.name)
    else:
        dobot.warning(f'Not recv from {esp.name}', esp.name)

    dobot.MovJJoint(position_1)
    time.sleep(2)

    dobot.RelMovLTool(0, -70, 0, 0, 0, 0, _v=50)
    time.sleep(2)

    dobot.Grab(False)
    dobot.MovLJoint(position_1)
    time.sleep(1)

    dobot.Pack()
    time.sleep(4)

    # dobot.DisableRobot()

    dobot.disconnect()
