import time

from filter import KalmanFilter
from motor import MixingMotor, StepperDirection, StepperMotor
from sensor import PHSensor
from uart import UARTWrapper


def do_mixing(mixing_motor: MixingMotor, ph_sensor: PHSensor, kalman_filter: KalmanFilter, uart: UARTWrapper):
    uart.send('MIX_START')

    mixing_motor.on()

    _counter = 0
    _times = 0

    while True:
        raw_ph = ph_sensor.read_ph()
        ph = kalman_filter.update(raw_ph)

        _counter += 1
        if _counter == 100:
            uart.send(f'pH:{ph:.2f}')
            _counter = 0
            _times += 1

        if _times >= 5:
            uart.send('MIX_DONE')
            break

        time.sleep(0.005)

    mixing_motor.off()


def do_injection(stepper_motor: StepperMotor, uart: UARTWrapper):
    uart.send('INJECT_START')

    delay_up = stepper_motor.set_rpm(100)
    stepper_motor.step(2000, delay_up, StepperDirection.UP)
    time.sleep(1)

    delay_down = stepper_motor.set_rpm(100)
    stepper_motor.step(2000, delay_down, StepperDirection.DOWN)
    time.sleep(1)

    uart.send('INJECT_DONE')


def main():
    uart = UARTWrapper(2, 115200)

    stepper_motor = StepperMotor(2, 4)

    mixing_motor = MixingMotor(32)

    ph_sensor = PHSensor(35)

    kalman_filter = KalmanFilter(7.0, 1.0, 0.01, 0.1)

    while True:
        try:
            data = uart.recv().upper()

            if not data:
                continue

            if data == 'START':
                uart.send('READY')

            if data == 'DO_MIX':
                do_mixing(mixing_motor, ph_sensor, kalman_filter, uart)

            if data == 'DO_INJECT':
                do_injection(stepper_motor, uart)

            if data == 'DONE':
                uart.send('DONE')
                # break

            time.sleep(0.1)

        except KeyboardInterrupt:
            break


if __name__ == '__main__':
    main()
    pass
