import time

from machine import ADC, Pin, time_pulse_us


class UltrasonicSensor:
    """Ultrasonic Distance Sensor with trigger and echo pins."""

    def __init__(self, triger_pin_id, echo_pin_id, sonic=291, signal_us=(2, 10), timeout=500 * 2 * 30):
        """Initialize the ultrasonic sensor with given pin IDs and parameters."""
        assert len(self.signal_us) == 2, 'signal_us must have exactly 2 elements: [zore_level_time, high_level_time]'

        self.trigger_pin = Pin(triger_pin_id, mode=Pin.OUT, pull=None)
        self.trigger_pin.value(0)
        self.echo_pin = Pin(echo_pin_id, mode=Pin.IN, pull=None)
        self.sonic = sonic  # Speed of sound in air in m/s
        self.signal_us = signal_us
        self.timeout = timeout

    def get_time_pulse_us(self):
        """Send ultrasonic pulse and measure the time until echo is received."""
        zore_level_time, high_level_time = self.signal_us

        self.trigger_pin.value(0)
        time.sleep_us(zore_level_time)
        self.trigger_pin.value(1)
        time.sleep_us(high_level_time)
        self.trigger_pin.value(0)

        return time_pulse_us(self.echo_pin, 1, self.timeout)

    def to_mm(self):
        """Return distance in millimeters."""
        pulse_time_us = self.get_time_pulse_us()

        if pulse_time_us < 0:
            print('Ultrasonic sensor timeout')
            return 0  # Indicate timeout

        mm = pulse_time_us * 100 / 2 / self.sonic

        print(f'UltrasonicSensor pulse time: {pulse_time_us}us, distance: {mm}mm')
        return mm

    def to_cm(self):
        """Return distance in centimeters."""
        return self.to_mm() / 10

    def value(self):
        """Return distance in centimeters."""
        return self.to_cm()


class TrackingPatterns:
    """Predefined tracking sensor patterns."""

    ON_PATH = (0, 0)
    LEFT_OFF_PATH = (0, 1)
    RIGHT_OFF_PATH = (1, 0)
    OFF_PATH = (1, 1)


class TrackingSensor:
    """Tracking Sensor with two digital inputs."""

    def __init__(self, left_pin_id, right_pin_id):
        """Initialize the tracking sensor with given left and right pin IDs."""
        self.left_pin = Pin(left_pin_id, Pin.IN)
        self.right_pin = Pin(right_pin_id, Pin.IN)

    def value(self):
        """Return the tracking sensor values as a tuple (left, right)."""
        left_value = self.left_pin.value()
        right_value = self.right_pin.value()

        print(f'TrackingSensor left: {left_value}, right: {right_value}')
        return left_value, right_value


class PHSensor:
    """pH Sensor connected to an analog pin."""

    def __init__(self, pin_id):
        """Initialize the pH sensor with given analog pin ID."""
        self.analog = ADC(Pin(pin_id))
        self.analog.init(atten=ADC.ATTN_11DB)  # Set full range to 3.3V

        print('[WARNING] The ADC reading method is unstable. Consider using an external ADC for better accuracy.')

    def value(self):
        """Return the pH sensor value as voltage."""
        voltage = self.analog.read_uv() / 1e6

        return voltage

    def read_v(self):
        """Return the voltage reading from the pH sensor."""
        return self.value()

    def read_ph(self, slope=-5.7541, intercept=16.5962):
        """Convert voltage to pH value."""
        return slope * self.read_v() + intercept


if __name__ == '__main__':
    # Example usage for the PHSensor with Kalman Filter
    from .filter import KalmanFilter

    ph_sensor = PHSensor(35)
    kalman_filter = KalmanFilter(7.0, 1.0, 0.01, 0.1)
    counter = 0
    while True:
        try:
            raw_v = ph_sensor.read_v()
            filtered_v = kalman_filter.update(raw_v)

            counter += 1
            if counter == 100:
                print(f'Filtered v: {filtered_v:.2f}')
                counter = 0
            time.sleep(0.005)

        except KeyboardInterrupt:
            break
