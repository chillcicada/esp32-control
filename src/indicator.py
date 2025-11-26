import time
from abc import ABC, abstractmethod

from machine import Pin


class Indicator(ABC):
    """Abstract base class for indicators like beepers and LEDs."""

    @abstractmethod
    def on(self):
        """Turn the indicator on."""
        pass

    @abstractmethod
    def off(self):
        """Turn the indicator off."""
        pass


class BeepIndicator(Indicator):
    """Beep Indicator using a digital output pin."""

    def __init__(self, pin_id=5):
        self.pin = Pin(pin_id, Pin.OUT)
        self.pin_id = pin_id
        print(f'Initializing BeepIndicator on pin {pin_id}')

    def on(self):
        """Turn the beep on."""
        self.pin.value(1)
        print(f'Beep ON on pin {self.pin_id}')

    def off(self):
        """Turn the beep off."""
        self.pin.value(0)
        print(f'Beep OFF on pin {self.pin_id}')

    def loop(self, count=3, delay=0.1):
        """Beep multiple times with a delay."""
        for _ in range(count):
            self.on()
            time.sleep(delay)
            self.off()
            time.sleep(delay)


class LEDIndicator(Indicator):
    """LED Indicator using a digital output pin."""

    def __init__(self, pin_id=2, period_ms=500):
        self.pin = Pin(pin_id, Pin.OUT)
        self.pin_id = pin_id
        self.period_ns = period_ms * 1_000_000  # Convert ms to ns
        self.last_toggle_time = 0
        self.state = False
        print(f'Initializing LEDIndicator on pin {pin_id} with period {period_ms}ms')

    def on(self):
        """Turn the LED on."""
        self.pin.value(1)
        print(f'LED ON on pin {self.pin_id}')

    def off(self):
        """Turn the LED off."""
        self.pin.value(0)
        print(f'LED OFF on pin {self.pin_id}')

    def toggle(self):
        """Toggle the LED state based on the defined period."""
        current_time = time.time_ns()
        if current_time - self.last_toggle_time >= self.period_ns:
            self.state = not self.state
            if self.state:
                self.on()
            else:
                self.off()
            self.last_toggle_time = current_time
            print(f'LED toggled to {"ON" if self.state else "OFF"} on pin {self.pin_id}')


if __name__ == '__main__':
    pass
