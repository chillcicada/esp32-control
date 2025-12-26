import time

from filter import KalmanFilter
from motor import MixingMotor, StepperDirection, StepperMotor
from sensor import PHSensor
from uart import UARTWrapper


def get_ph(ph_sensor: PHSensor, kalman_filter: KalmanFilter) -> float:
    raw_ph = ph_sensor.read_ph()
    ph = kalman_filter.update(raw_ph)

    _counter = 0
    while _counter < 100:
        raw_ph = ph_sensor.read_ph()
        ph = kalman_filter.update(raw_ph)
        _counter += 1
        time.sleep(0.005)

    return ph


def do_mix(mixing_motor: MixingMotor, ph_sensor: PHSensor, kalman_filter: KalmanFilter, uart: UARTWrapper):
    uart.send('MIX_START')

    mixing_motor.on()

    sensor_counter = 0
    values_counter = 0
    last_ph = 0.0

    while sensor_counter < 50000:
        raw_ph = ph_sensor.read_ph()
        ph = kalman_filter.update(raw_ph)

        if abs(ph - last_ph) <= 0.05:
            values_counter += 1
        else:
            values_counter = 0

        if values_counter >= 10:
            uart.send(f'PH_STABLE_AT:{ph:.2f}')
            break

        last_ph = ph
        sensor_counter += 1
        time.sleep(0.001)

    time.sleep(1)
    uart.send('MIX_DONE')

    mixing_motor.off()


def do_inject(stepper_motor: StepperMotor, uart: UARTWrapper):
    uart.send('STEPPER_START')

    while True:
        data = uart.recv()
        if data.startswith('SET_STEPPER'):
            data = data.split(':', 1)[1]
            rpm, steps, direction = data.split(',')
            if rpm.isdigit() and steps.isdigit() and direction in ('UP', 'DOWN'):
                data = f'RPM={rpm},STEPS={steps},DIR={direction}'
                uart.send(f'STEPPER_CONFIGURED:{data}')
                break
            else:
                uart.send('STEPPER_CONFIG_INVALID')
        elif data:
            uart.send('STEPPER_RECV_INVALID')

    rpm = int(rpm)
    steps = int(steps)
    stepper_dir = StepperDirection.UP if direction == 'UP' else StepperDirection.DOWN

    if steps <= 0:
        time.sleep(1)
        uart.send('STEPPER_DONE')
        return

    delay_up = stepper_motor.set_rpm(rpm)
    stepper_motor.step(steps, delay_up, stepper_dir)

    time.sleep(1)
    uart.send('STEPPER_DONE')


def main():
    uart = UARTWrapper(2, 115200)
    stepper_motor = StepperMotor(2, 4)
    mixing_motor = MixingMotor(32)
    ph_sensor = PHSensor(35)
    kalman_filter = KalmanFilter(7.0, 1.0, 0.01, 0.1)

    while True:
        try:
            cmd = uart.recv().upper()

            if not cmd:
                continue

            elif cmd == 'PING':
                uart.send('PONG')

            elif cmd == 'GET_MAX_STEPS':
                max_steps = stepper_motor.get_max_steps()
                uart.send(f'MAX_STEPS:{max_steps}')

            elif cmd == 'GET_PH':
                ph = get_ph(ph_sensor, kalman_filter)
                uart.send(f'pH:{ph:.2f}')

            elif cmd == 'START':
                uart.send('READY')

            elif cmd == 'DO_MIX':
                do_mix(mixing_motor, ph_sensor, kalman_filter, uart)

            elif cmd == 'DO_INJECT':
                do_inject(stepper_motor, uart)

            elif cmd == 'DONE':
                uart.send('DONE')
                # break

            time.sleep(0.1)

        except KeyboardInterrupt:
            break


if __name__ == '__main__':
    main()
    pass
