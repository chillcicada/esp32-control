import time

from machine import Pin


class PS2Protocol:
    def __init__(self, dat_pin, cmd_pin, sel_pin, clk_pin):
        self.dat = Pin(dat_pin, Pin.IN, Pin.PULL_UP)
        self.cmd = Pin(cmd_pin, Pin.OUT)
        self.sel = Pin(sel_pin, Pin.OUT)
        self.clk = Pin(clk_pin, Pin.OUT)

        self.cmd.value(1)
        self.clk.value(1)
        self.sel.value(1)

    def shift_io(self, byte_out, delay_us=5):
        byte_in = 0

        for i in range(8):
            self.cmd.value(byte_out & (1 << i))
            self.clk.value(0)
            time.sleep_us(delay_us)

            if self.dat.value():
                byte_in |= 1 << i

            self.clk.value(1)
            time.sleep_us(delay_us)

        self.cmd.value(1)
        time.sleep_us(delay_us)

        return byte_in

    def start(self, delay_us=5):
        self.sel.value(0)
        time.sleep_us(delay_us)

    def end(self, delay_us=1):
        self.sel.value(1)
        time.sleep_us(delay_us)

    def send_cmd(self, cmd_bytes, io_delay_us=5, start_delay_us=5, end_delay_us=1):
        self.start(start_delay_us)
        print(f'Sending command: {[hex(b) for b in cmd_bytes]}')

        res_bytes = []
        for byte in cmd_bytes:
            res_bytes.append(self.shift_io(byte, io_delay_us))

        print(f'Received response: {[hex(b) for b in res_bytes]}')
        self.end(end_delay_us)

        return res_bytes


class PS2Commands:
    INIT = [0x01, 0x43, 0x00, 0x01, 0x00]
    READ = [0x01, 0x42, 0x00]
    EXIT = [0x01, 0x43, 0x00, 0x00, 0x5A, 0x5A, 0x5A]
    ENABLE_RUMBLE = [0x01, 0x4D, 0x00, 0x00, 0x01]
    ENABLE_PRESSURES = [0x01, 0x4F, 0x00, 0xFF, 0xFF, 0x03, 0x00, 0x00, 0x00]


class PS2ButtonState:
    def __init__(self):
        self.current_state = 0
        self.previous_state = 0

    def update(self, new_state):
        self.previous_state = self.current_state
        self.current_state = new_state

    def is_pressed(self, button_mask):
        return not (self.current_state & button_mask)

    def is_released(self, button_mask):
        return not (self.current_state & button_mask)

    def has_changed(self, button_mask=None):
        if button_mask:
            return (self.previous_state & button_mask) != (self.current_state & button_mask)

        return self.previous_state != self.current_state

    def was_pressed(self, button_mask):
        return self.is_pressed(button_mask) and self.has_changed(button_mask)

    def was_released(self, button_mask):
        return self.is_released(button_mask) and self.has_changed(button_mask)


#     READ_INPUT = [0x01, 0x42, 0x00]
#     ENTER_CONFIG = [0x01, 0x43, 0x00, 0x01, 0x00]
#     EXIT_CONFIG = [0x01, 0x43, 0x00, 0x00, 0x5A, 0x5A, 0x5A]

#     SET_MODE_ANALOG = [0x01, 0x44, 0x00, 0x01, 0x03, 0x00, 0x00, 0x00, 0x00]


class PS2Buttons:
    SELECT = 0x0001
    L3 = 0x0002
    R3 = 0x0004
    START = 0x0008
    UP = 0x0010
    RIGHT = 0x0020
    DOWN = 0x0040
    LEFT = 0x0080
    L2 = 0x0100
    R2 = 0x0200
    L1 = 0x0400
    R1 = 0x0800
    TRIANGLE = 0x1000
    CIRCLE = 0x2000
    CROSS = 0x4000
    SQUARE = 0x8000


class PS2Controller:
    def __init__(self, protocol, button_state):
        self.protocol = protocol
        self.button_state = button_state

        self.analog_buffer = []
        self.controller_type = 0

        self.enabled_rumble = False
        self.enabled_pressures = False

        self._last_state_time = 0

    def get_analog(self, index):
        return self.analog_buffer[index]

    def _perform_read_cycle(self, motor1, motor2, retry_count=5):
        pass


class PS2ControllerWrapper:
    @staticmethod
    def create(dat_pin, cmd_pin, sel_pin, clk_pin):
        protocol = PS2Protocol(dat_pin, cmd_pin, sel_pin, clk_pin)
        button_state = PS2ButtonState()

        controller = PS2Controller(protocol, button_state)
        print('Initialized PS2ControllerWrapper')

        return controller
