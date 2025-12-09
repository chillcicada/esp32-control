import threading

from maix import app, camera, display, pinmap, time, uart

stuts0 = ''
stuts1 = ''

# 摄像头初始化
cam = camera.Camera(1024, 960)
disp = display.Display()


def re_uart(serial):
    global stuts0, stuts1, serial0, serial1
    while 1:
        # 串口  接收数据
        data = serial.read()
        data = data.decode('utf-8', errors='ignore')
        if data != '' and serial == serial0:  # 串口0 赋值
            #   print(data)
            stuts0 = data
            data = ''
        if data != '' and serial == serial1:  # 串口1 赋值
            stuts1 = data
            data = ''


# 串口初始化
pinmap.set_pin_function('A29', 'UART2_RX')
pinmap.set_pin_function('A28', 'UART2_TX')
device = '/dev/ttyS0'
serial0 = uart.UART(device, 115200)
device = '/dev/ttyS2'
serial1 = uart.UART(device, 115200)

uart0_thread = threading.Thread(target=re_uart, args=(serial0,))
uart0_thread.daemon = True
uart0_thread.start()

uart1_thread = threading.Thread(target=re_uart, args=(serial1,))
uart1_thread.daemon = True
uart1_thread.start()


while not app.need_exit():
    img = cam.read()
    disp.show(img)
    time.sleep(2)
    u_id = 'biao'
    x_zb = int(30.5)
    y_zb = int(31)
    z_zb = int(-20.12345131)
    u_data = f'{u_id}{x_zb:04d}{y_zb:04d}{z_zb:04d}'.encode('utf-8')
    serial0.write_str(u_data)

    if stuts0 != '':
        serial0.write_str(f'uart0:{stuts0}')
        stuts0 = ''

    if stuts1 != '':
        serial1.write_str(f'uart0:{stuts1}')
        stuts1 = ''
