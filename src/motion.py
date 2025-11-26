import time
from warnings import deprecated

from machine import PWM, Pin

MIN_PWM = 1000
MAX_PWM = 2000
BASE_PWM = 1500


class MotionController:
    """Motion Controller for Robot Car"""

    def __init__(self, pin_ids, freq):
        """Initialize PWM on given pin IDs with specified frequency."""
        self.pwms = [PWM(Pin(pin_id), freq=freq, duty=0) for pin_id in pin_ids]
        self.freq = freq

    def set_freq(self, freq):
        """Set PWM frequency for all pins."""
        self.freq = freq
        for pwm in self.pwms:
            pwm.freq(self.freq)
        print(f'Set PWM frequency to {freq}Hz for all pins')

    def set_duty(self, pin_index, pwm):
        """Set duty cycle for a specific pin index based on PWM value."""
        if 0 <= pin_index < len(self.pwms):
            pwm = max(MIN_PWM, min(MAX_PWM, pwm))
            duty = int((pwm * 65535) / (1000000 / self.freq))

            self.pwms[pin_index].duty_u16(duty)

            print(f'Set duty cycle of pin index {pin_index} to {duty} (PWM {pwm})')
        else:
            print(f'Pin index {pin_index} out of range')

    def release(self):
        """Deinitialize all PWM pins."""
        for pwm in self.pwms:
            pwm.deinit()

        print('Deinitialized all PWM pins')


class MotionPatterns:
    """Predefined motion patterns for the robot car."""

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
    """Wrapper for MotionController with high-level movement methods."""

    def __init__(self, pin_ids, freq=50):
        """Initialize the MotionController with given pin IDs and frequency."""
        self.controller = MotionController(pin_ids, freq)

    def start(self, delay=5):
        """Gradually start all motors to base PWM."""
        for i in range(4):
            self.controller.set_duty(i, MIN_PWM)

        print('MotionController started at stage 1')

        time.sleep(delay)

        for i in range(4):
            self.controller.set_duty(i, BASE_PWM)

        print('MotionController started at stage 2')

        time.sleep(1)

    def stop(self, sleep_time=0):
        """Stop all motors by setting them to base PWM."""
        for i in range(4):
            self.controller.set_duty(i, BASE_PWM)

        if sleep_time > 0:
            time.sleep(sleep_time)

        print('MotionController stopped all motors')

    def release(self):
        """Deinitialize the motion controller."""
        self.controller.release()

        print('MotionController deinitialized')

    def move(self, pattern, speed_pwm=0, callback=None):
        """Move the robot using the specified motion pattern and speed."""
        assert len(pattern) == 4, 'Pattern must have exactly 4 elements.'

        for i, sign in enumerate(pattern):
            self.controller.set_duty(i, BASE_PWM + sign * speed_pwm)

        print(f'MotionController move called with pattern {pattern} and speed {speed_pwm}')

        if callback:
            callback()

    @deprecated('Use move() method instead.')
    def forward(self, speed_pwm=0, callback=None):
        """Move the car forward."""
        self.move(MotionPatterns.FORWARD, speed_pwm, callback)

    @deprecated('Use move() method instead.')
    def backward(self, speed_pwm=0, callback=None):
        """Move the car backward."""
        self.move(MotionPatterns.BACKWARD, speed_pwm, callback)

    @deprecated('Use move() method instead.')
    def left(self, speed_pwm=0, callback=None):
        """Move the car left."""
        self.move(MotionPatterns.LEFT, speed_pwm, callback)

    @deprecated('Use move() method instead.')
    def right(self, speed_pwm=0, callback=None):
        """Move the car right."""
        self.move(MotionPatterns.RIGHT, speed_pwm, callback)

    @deprecated('Use move() method instead.')
    def left_forward(self, speed_pwm=0, callback=None):
        """Move the car left forward."""
        self.move(MotionPatterns.LEFT_FORWARD, speed_pwm, callback)

    @deprecated('Use move() method instead.')
    def right_forward(self, speed_pwm=0, callback=None):
        """Move the car right forward."""
        self.move(MotionPatterns.RIGHT_FORWARD, speed_pwm, callback)

    @deprecated('Use move() method instead.')
    def left_backward(self, speed_pwm=0, callback=None):
        """Move the car left backward."""
        self.move(MotionPatterns.LEFT_BACKWARD, speed_pwm, callback)

    @deprecated('Use move() method instead.')
    def right_backward(self, speed_pwm=0, callback=None):
        """Move the car right backward."""
        self.move(MotionPatterns.RIGHT_BACKWARD, speed_pwm, callback)

    @deprecated('Use move() method instead.')
    def left_rotation(self, speed_pwm=0, callback=None):
        """Rotate the car left."""
        self.move(MotionPatterns.LEFT_ROTATION, speed_pwm, callback)

    @deprecated('Use move() method instead.')
    def right_rotation(self, speed_pwm=0, callback=None):
        """Rotate the car right."""
        self.move(MotionPatterns.RIGHT_ROTATION, speed_pwm, callback)

    @deprecated('Use move() method instead.')
    def left_deflection(self, speed_pwm=0, callback=None):
        """Deflect the car to the left."""
        self.move(MotionPatterns.LEFT_DEFLECTION, speed_pwm, callback)

    @deprecated('Use move() method instead.')
    def right_deflection(self, speed_pwm=0, callback=None):
        """Deflect the car to the right."""
        self.move(MotionPatterns.RIGHT_DEFLECTION, speed_pwm, callback)


if __name__ == '__main__':
    # Example usage for the MotionWrapper
    pin_ids = [32, 33, 25, 26]
    motion = MotionWrapper(pin_ids, freq=50)
    motion.start(delay=5)

    def callback():
        time.sleep(10)
        motion.stop(sleep_time=3)

    motion.move(MotionPatterns.FORWARD, speed_pwm=200, callback=callback)
    motion.move(MotionPatterns.BACKWARD, speed_pwm=200, callback=callback)
    motion.move(MotionPatterns.LEFT, speed_pwm=200, callback=callback)
    motion.move(MotionPatterns.RIGHT, speed_pwm=200, callback=callback)
    motion.move(MotionPatterns.LEFT_FORWARD, speed_pwm=200, callback=callback)
    motion.move(MotionPatterns.RIGHT_FORWARD, speed_pwm=200, callback=callback)
    motion.move(MotionPatterns.LEFT_BACKWARD, speed_pwm=200, callback=callback)
    motion.move(MotionPatterns.RIGHT_BACKWARD, speed_pwm=200, callback=callback)
    motion.move(MotionPatterns.LEFT_ROTATION, speed_pwm=200, callback=callback)
    motion.move(MotionPatterns.RIGHT_ROTATION, speed_pwm=200, callback=callback)
    motion.move(MotionPatterns.LEFT_DEFLECTION, speed_pwm=200, callback=callback)
    motion.move(MotionPatterns.RIGHT_DEFLECTION, speed_pwm=200, callback=callback)

    motion.release()
