from .motion import MotionPatterns, MotionWrapper
from .ps2 import PS2ControllerWrapper
from .sensor import TrackingPatterns, TrackingSensor, UltrasonicSensor
from .uart import UARTWrapper


class CentralController:
    def __init__(
        self,
        motion: MotionWrapper,
        ps2_controller: PS2ControllerWrapper,
        tracking: TrackingSensor,
        ultrasonic: UltrasonicSensor,
        uart: UARTWrapper,
    ):
        self.motion = motion

        self.ps2_controller = ps2_controller

        self.tracking = tracking
        self.ultrasonic = ultrasonic

        self.uart = uart

    def free_obstacle_avoidance(self, speed_pwm: int, stop_time: float):
        distance = self.ultrasonic.to_cm()

        if not distance:
            print('Ultrasonic sensor read failed.')
            return

        if distance < 40:
            self.motion.stop(stop_time)

        else:
            self.motion.set_speed(speed_pwm)
            self.motion.forward(stop_time)

    def tracking_path(self, speed_pwm: int):
        tracking_value = self.tracking.value()

        if tracking_value == TrackingPatterns.LEFT_OFF_PATH:
            self.motion.move(MotionPatterns.RIGHT_DEFLECTION, speed_pwm)
        elif tracking_value == TrackingPatterns.RIGHT_OFF_PATH:
            self.motion.move(MotionPatterns.LEFT_ROTATION, speed_pwm)
        elif tracking_value == TrackingPatterns.ON_PATH:
            self.motion.move(MotionPatterns.FORWARD, speed_pwm)
        elif tracking_value == TrackingPatterns.OFF_PATH:
            self.motion.stop()

    def manual_control(self):
        # TODO
        command = self.ps2_controller.read_command()

        if command == 'FORWARD':
            self.motion.move(MotionPatterns.FORWARD, self.ps2_controller.speed_pwm)
        elif command == 'BACKWARD':
            self.motion.move(MotionPatterns.BACKWARD, self.ps2_controller.speed_pwm)
        elif command == 'LEFT':
            self.motion.move(MotionPatterns.LEFT_ROTATION, self.ps2_controller.speed_pwm)
        elif command == 'RIGHT':
            self.motion.move(MotionPatterns.RIGHT_ROTATION, self.ps2_controller.speed_pwm)
        elif command == 'STOP':
            self.motion.stop()
        else:
            print(f'Unknown PS2 command: {command}')


if __name__ == '__main__':
    pass
