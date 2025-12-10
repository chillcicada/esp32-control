import threading

from maix import app, pinmap, uart


pinmap.set_pin_function('A29', 'UART2_RX')
pinmap.set_pin_function('A28', 'UART2_TX')
serial_esp = uart.UART('/dev/ttyS2', 115200)

stuts1 = ''


def re_uart(serial):
    global stuts1
    while 1:
        # 串口  接收数据
        data = serial.read()
        data = data.decode(errors='ignore').strip()
        if data != '':  # 串口1 赋值
            stuts1 = data
            data = ''

uart1_thread = threading.Thread(target=re_uart, args=(serial_esp,))
uart1_thread.daemon = True
uart1_thread.start()


while not app.need_exit():
    # get the data from stuts1
    if stuts1 != '':
        print(stuts1)
        stuts1 = ''
