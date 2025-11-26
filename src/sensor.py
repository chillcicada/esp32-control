import time
from abc import ABC, abstractmethod

from machine import ADC, Pin, time_pulse_us


class Sensor(ABC):
    """Abstract base class for sensors."""

    @abstractmethod
    def value(self):
        """Return the sensor value."""
        pass


class UltrasonicSensor(Sensor):
    """Ultrasonic Distance Sensor with trigger and echo pins."""

    def __init__(self, triger_pin_number, echo_pin_number, sonic=291, signal_us=(2, 10), timeout=500 * 2 * 30):
        assert len(self.signal_us) == 2, 'signal_us must have exactly 2 elements: [zore_level_time, high_level_time]'

        self.trigger = Pin(triger_pin_number, mode=Pin.OUT, pull=None)
        self.trigger.value(0)
        self.echo = Pin(echo_pin_number, mode=Pin.IN, pull=None)
        self.sonic = sonic  # Speed of sound in air in m/s
        self.signal_us = signal_us
        self.timeout = timeout

    def get_time_pulse_us(self):
        """Send ultrasonic pulse and measure the time until echo is received."""
        zore_level_time, high_level_time = self.signal_us

        self.trigger.value(0)
        time.sleep_us(zore_level_time)
        self.trigger.value(1)
        time.sleep_us(high_level_time)
        self.trigger.value(0)

        return time_pulse_us(self.echo, 1, self.timeout)

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


class TrackingSensor(Sensor):
    """Tracking Sensor with two digital inputs."""

    def __init__(self, left_pin_number, right_pin_number):
        self.left_sensor = Pin(left_pin_number, Pin.IN)
        self.right_sensor = Pin(right_pin_number, Pin.IN)

    def value(self):
        """Return the tracking sensor values as a tuple (left, right)."""
        left_value = self.left_sensor.value()
        right_value = self.right_sensor.value()

        print(f'TrackingSensor left: {left_value}, right: {right_value}')
        return left_value, right_value


class PHSensor(Sensor):
    """pH Sensor connected to an analog pin."""

    def __init__(self, analog_pin):
        self.analog = ADC(Pin(analog_pin))
        self.analog.init(atten=ADC.ATTN_11DB)  # Set full range to 3.3V

    def value(self):
        """Return the pH sensor value as voltage."""
        raw_value = self.analog.read_u16()
        voltage = raw_value * 3.3 / 4095  # Convert to voltage (0-3.3V)

        print(f'PHSensor analog value: {raw_value}, voltage: {voltage:.2f}V')
        return voltage
