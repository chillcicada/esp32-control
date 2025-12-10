import time

from filter import KalmanFilter
from motor import MixingMotor, StepperMotor
from sensor import PHSensor
from uart import UARTWrapper


def do_mixing(mixing_motor: MixingMotor, ph_sensor: PHSensor, kalman_filter: KalmanFilter):
    mixing_motor.on()

    _counter = 0

    _times = 0

    while True:
        raw_v = ph_sensor.read_v()
        filtered_v = kalman_filter.update(raw_v)

        _counter += 1
        if _counter == 100:
            print(f'Filtered v: {filtered_v:.2f}')
            _counter = 0
            _times += 1
        time.sleep(0.005)

        if _times >= 5:
            break

    mixing_motor.off()


def main():
    uart = UARTWrapper(2, 115200)

    stepper_motor = StepperMotor(2, 4)

    mixing_motor = MixingMotor(32)

    ph_sensor = PHSensor(35)

    kalman_filter = KalmanFilter(7.0, 1.0, 0.01, 0.1)

    while True:
        try:
            data = uart.recv()

            if not data:
                continue

            print('data:', data)

            if data.find('MIX') != -1:
                print('Starting mixing operation...')
                do_mixing(mixing_motor, ph_sensor, kalman_filter)
                print('Mixing operation completed.')

        except KeyboardInterrupt:
            break


if __name__ == '__main__':
    main()
