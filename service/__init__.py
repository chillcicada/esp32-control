from maix import pinmap, uart


pinmap.set_pin_function('A29', 'UART2_RX')
pinmap.set_pin_function('A28', 'UART2_TX')
serial_esp = uart.UART('/dev/ttyS2', 115200)

serial_esp.write(b'MIX')
