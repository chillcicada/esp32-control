import time

from machine import Pin


class StepperDirection:
    """Stepper Motor Direction Enum"""

    UP = 0
    DOWN = 1


class StepperMotor:
    """UM242 Stepper Motor Driver"""

    def __init__(self, pul_pin_id, dir_pin_id, steps_per_rev=200):
        """Initialize the stepper motor with given pin IDs and steps per revolution."""
        self.pul_pin = Pin(pul_pin_id, Pin.OUT)
        self.dir_pin = Pin(dir_pin_id, Pin.OUT)
        self.steps_per_rev = steps_per_rev
        self.current_position = 0

        self.pul_pin.value(0)
        self.dir_pin.value(0)

    def step(self, steps, delay_us=500, direction=None):
        """Move the motor by a specific number of steps."""
        if direction is not None:
            self.dir_pin.value(direction)
            time.sleep_us(20)

        actual_direction = self.dir_pin.value()

        print(f'Moving {"UP" if actual_direction == StepperDirection.UP else "DOWN"} by {steps} steps')

        for _ in range(steps):
            self.pul_pin.value(1)
            time.sleep_us(10)
            self.pul_pin.value(0)
            time.sleep_us(delay_us)

        self.current_position += steps if actual_direction == StepperDirection.UP else -steps

    def move_angle(self, angle, delay_us=500, direction=None):
        """Move the motor by a specific angle."""
        steps = int(angle / 360 * self.steps_per_rev)
        self.step(steps, delay_us, direction)

    def move_to_angle(self, target_angle, delay_us=500):
        """Move to the specific angle."""
        current_angle = (self.current_position % self.steps_per_rev) * 360 / self.steps_per_rev
        angle_diff = (target_angle - current_angle + 180) % 360 - 180
        self.move_angle(angle_diff, delay_us, direction=1 if angle_diff >= 0 else 0)

    def set_rpm(self, rpm):
        """Set motor speed in RPM and return pulse interval in microseconds."""
        assert rpm > 0, 'RPM must be positive!'

        print(f'Setting motor speed to {rpm} RPM')

        interval = max(60 * 1000000 / (self.steps_per_rev * rpm), 20)
        print(f'Pulse interval set to {interval} us')
        return interval

    def get_position(self):
        """Get the current position in steps."""
        return self.current_position

    def reset_position(self):
        """Reset the current position to zero."""
        self.current_position = 0


if __name__ == '__main__':
    # Example usage of StepperMotor
    stepper_motor = StepperMotor(2, 4)

    delay_up = stepper_motor.set_rpm(100)
    stepper_motor.step(4000, delay_up, StepperDirection.UP)
    time.sleep(1)

    delay_down = stepper_motor.set_rpm(10)
    stepper_motor.step(4000, delay_down, StepperDirection.DOWN)
    time.sleep(1)
