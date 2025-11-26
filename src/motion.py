import time

from machine import PWM, Pin

MIN_PWM = 1000
MAX_PWM = 2000
BASE_PWM = 1500


class MotionController:
    def __init__(self, pins, freq=1000):
        self.pwms = [PWM(Pin(pin), freq=freq, duty=0) for pin in pins]
        self.freq = freq
        print(f'Initialized PWMController with pins {pins} at frequency {freq}Hz')

    def set_freq(self, freq):
        self.freq = freq
        for pwm in self.pwms:
            pwm.freq(self.freq)
        print(f'Set PWM frequency to {freq}Hz for all pins')

    def set_duty(self, pin_index, pwm):
        if 0 <= pin_index < len(self.pwms):
            pwm = max(MIN_PWM, min(MAX_PWM, pwm))
            duty = int((pwm * 65535) / (1000000 / self.freq))

            self.pwms[pin_index].duty_u16(duty)
            print(f'Set duty cycle of pin index {pin_index} to {duty} (PWM {pwm})')
        else:
            print(f'Pin index {pin_index} out of range')

    def stop(self):
        for pwm in self.pwms:
            pwm.deinit()
        print('Deinitialized all PWM pins')


class MotionPatterns:
    FORWARD = [1, -1, 1, -1]
    BACKWARD = [-1, 1, -1, 1]
    LEFT = [-1, -1, 1, 1]
    RIGHT = [1, 1, -1, -1]
    LEFT_FORWARD = [0, -1, 1, 0]
    RIGHT_FORWARD = [1, 0, 0, -1]
    LEFT_BACKWARD = [0, 1, -1, 0]
    RIGHT_BACKWARD = [-1, 0, 0, 1]
    LEFT_ROTATION = [-1, -1, -1, -1]
    RIGHT_ROTATION = [1, 1, 1, 1]
    LEFT_DEFLECTION = [0, 0, -1, -1]
    RIGHT_DEFLECTION = [1, 1, 0, 0]


class MotionWrapper:
    def __init__(self, pins, freq=50):
        self.controller = MotionController(pins, freq)
        print(f'Initialized MotionController with pins {pins} at frequency {freq}Hz')

    def start(self, delay=5):
        for i in range(4):
            self.controller.set_duty(i, MIN_PWM)

        print('MotionController started at stage 1')

        time.sleep(delay)

        for i in range(4):
            self.controller.set_duty(i, BASE_PWM)

        print('MotionController started at stage 2')

        time.sleep(1)

    def stop(self, sleep_time=0):
        for i in range(4):
            self.controller.set_duty(i, BASE_PWM)

        if sleep_time > 0:
            time.sleep(sleep_time)

        print('MotionController stopped all motors')

    def move(self, pattern, speed_pwm=0, callback=None):
        assert len(pattern) == 4, 'Pattern must have exactly 4 elements.'

        for i, sign in enumerate(pattern):
            self.controller.set_duty(i, BASE_PWM + sign * speed_pwm)

        print(f'MotionController move called with pattern {pattern} and speed {speed_pwm}')

        if callback:
            callback()
