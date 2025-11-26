from .core import UARTWrapper
from .indicator import BeepIndicator, LEDIndicator


def main():
    beep = BeepIndicator()
    led = LEDIndicator()

    uart_controller = UARTWrapper(2)

    beep.loop(3, 0.1)
    print('Beep indicator initialized and beeped 3 times.')
