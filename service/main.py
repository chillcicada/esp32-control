# from conn import SerialConn
# from dobot import Dobot
from maix import app, display, image, pinmap, touchscreen

# init display and touchscreen
disp = display.Display()
touch = touchscreen.TouchScreen()

# define constants
MAIX_CAM_WIDTH = disp.width()
MAIX_CAM_HEIGHT = disp.height()

GRID22_WIDTH = MAIX_CAM_WIDTH // 2
GRID22_HEIGHT = MAIX_CAM_HEIGHT // 2

GRID44_WIDTH = MAIX_CAM_WIDTH // 4
GRID44_HEIGHT = MAIX_CAM_HEIGHT // 4

# create screen image
screen = image.Image(MAIX_CAM_WIDTH, MAIX_CAM_HEIGHT)

# load and set default font
# run `scp /path/to/MapleMono-Regular.ttf root@10.177.150.1:~/fonts` to upload font file
image.load_font('Maple Mono', '/root/fonts/MapleMono-Regular.ttf', 40)
image.set_default_font('Maple Mono')

# init UART0 for communication with dobot arm
# dobot = Dobot('/dev/ttyS0', isSerial=True)

# init UART2 for communication with embedded ESP32
pinmap.set_pin_function('A29', 'UART2_RX')
pinmap.set_pin_function('A28', 'UART2_TX')
# esp = SerialConn('ESP32')

# define the positions for dobot arm
station_1 = [-170, -30, -90, -60, -80, 0]
station_2 = [-130, -30, -90, -60, -40, 0]

position_1 = [-160, -30, -80, -70, 20, 0]
position_2 = [-140, -30, -80, -70, -140, 0]

# define input state
input_ph_str = ''

set_ph_val = -1.0
get_ph_val = -1.0


# define current state
class State:
    INIT = 'INIT'
    HOME = 'HOME'
    STEP = 'STEP'
    EXEC = 'EXEC'
    INPUT = 'INPUT'
    MESSAGE = 'MESSAGE'


curr_state = State.INIT
prev_state = State.INIT

# define touch state
last_x = 0
last_y = 0
last_pressed = 0

# region btns

#    single
# +---------+
# | msg btn |
# +---------+

btn_msg_pos = [0, MAIX_CAM_HEIGHT // 4, MAIX_CAM_WIDTH, MAIX_CAM_HEIGHT // 2]

#     2x2 grid
# +------+------+
# | btn1 | btn2 |
# +------+------+
# | btn3 | btn4 |
# +------+------+

btn_lt_label = 'EXEC'
btn_rt_label = 'STEP'
btn_lb_label = 'MORE'
btn_rb_label = 'EXIT'

btn_lt_pos = [0, 0, GRID22_WIDTH, GRID22_HEIGHT]
btn_rt_pos = [GRID22_WIDTH, 0, GRID22_WIDTH, GRID22_HEIGHT]
btn_lb_pos = [0, GRID22_HEIGHT, GRID22_WIDTH, GRID22_HEIGHT]
btn_rb_pos = [GRID22_WIDTH, GRID22_HEIGHT, GRID22_WIDTH, GRID22_HEIGHT]

#          4x4 grid
# +-----+-----+-----+-----+
# |  ×  |           |  ✓  |
# +-----+-----+-----+-----+
# |  1  |  2  |  3  |  4  |
# +-----+-----+-----+-----+
# |  5  |  6  |  7  |  8  |
# +-----+-----+-----+-----+
# |  9  |  0  |  .  | DEL |
# +-----+-----+-----+-----+

btn_00_pos = [0, 0, GRID44_WIDTH, GRID44_HEIGHT]
btn_01_pos = [GRID44_WIDTH, 0, GRID44_WIDTH, GRID44_HEIGHT]
btn_02_pos = [GRID44_WIDTH * 2, 0, GRID44_WIDTH, GRID44_HEIGHT]
btn_30_pos = [GRID44_WIDTH * 3, 0, GRID44_WIDTH, GRID44_HEIGHT]
btn_01_pos = [0, GRID44_HEIGHT, GRID44_WIDTH, GRID44_HEIGHT]
btn_11_pos = [GRID44_WIDTH, GRID44_HEIGHT, GRID44_WIDTH, GRID44_HEIGHT]
btn_21_pos = [GRID44_WIDTH * 2, GRID44_HEIGHT, GRID44_WIDTH, GRID44_HEIGHT]
btn_31_pos = [GRID44_WIDTH * 3, GRID44_HEIGHT, GRID44_WIDTH, GRID44_HEIGHT]
btn_02_pos = [0, GRID44_HEIGHT * 2, GRID44_WIDTH, GRID44_HEIGHT]
btn_12_pos = [GRID44_WIDTH, GRID44_HEIGHT * 2, GRID44_WIDTH, GRID44_HEIGHT]
btn_22_pos = [GRID44_WIDTH * 2, GRID44_HEIGHT * 2, GRID44_WIDTH, GRID44_HEIGHT]
btn_32_pos = [GRID44_WIDTH * 3, GRID44_HEIGHT * 2, GRID44_WIDTH, GRID44_HEIGHT]
btn_03_pos = [0, GRID44_HEIGHT * 3, GRID44_WIDTH, GRID44_HEIGHT]
btn_13_pos = [GRID44_WIDTH, GRID44_HEIGHT * 3, GRID44_WIDTH, GRID44_HEIGHT]
btn_23_pos = [GRID44_WIDTH * 2, GRID44_HEIGHT * 3, GRID44_WIDTH, GRID44_HEIGHT]
btn_33_pos = [GRID44_WIDTH * 3, GRID44_HEIGHT * 3, GRID44_WIDTH, GRID44_HEIGHT]

# endregion


def draw_btns_home(scale=2):
    draw_centered_text(btn_lt_label, scale=scale, offset_x=-GRID44_WIDTH, offset_y=-GRID44_HEIGHT)
    draw_centered_text(btn_rt_label, scale=scale, offset_x=GRID44_WIDTH, offset_y=-GRID44_HEIGHT)
    draw_centered_text(btn_lb_label, scale=scale, offset_x=-GRID44_WIDTH, offset_y=GRID44_HEIGHT)
    draw_centered_text(btn_rb_label, scale=scale, offset_x=GRID44_WIDTH, offset_y=GRID44_HEIGHT)


def draw_btns_input(scale=2):
    draw_centered_text('×', scale=scale, offset_x=-GRID44_WIDTH * 3 // 2, offset_y=-GRID44_HEIGHT * 3 // 2)
    draw_centered_text('✓', scale=scale, offset_x=GRID44_WIDTH * 3 // 2, offset_y=-GRID44_HEIGHT * 3 // 2)

    draw_centered_text(input_ph_str or '<Input>', image.COLOR_WHITE, scale, offset_y=-GRID44_HEIGHT * 3 // 2)

    draw_centered_text('1', scale=scale, offset_x=-GRID44_WIDTH * 3 // 2, offset_y=-GRID44_HEIGHT // 2)
    draw_centered_text('2', scale=scale, offset_x=-GRID44_WIDTH // 2, offset_y=-GRID44_HEIGHT // 2)
    draw_centered_text('3', scale=scale, offset_x=GRID44_WIDTH // 2, offset_y=-GRID44_HEIGHT // 2)
    draw_centered_text('4', scale=scale, offset_x=GRID44_WIDTH * 3 // 2, offset_y=-GRID44_HEIGHT // 2)
    draw_centered_text('5', scale=scale, offset_x=-GRID44_WIDTH * 3 // 2, offset_y=GRID44_HEIGHT // 2)
    draw_centered_text('6', scale=scale, offset_x=-GRID44_WIDTH // 2, offset_y=GRID44_HEIGHT // 2)
    draw_centered_text('7', scale=scale, offset_x=GRID44_WIDTH // 2, offset_y=GRID44_HEIGHT // 2)
    draw_centered_text('8', scale=scale, offset_x=GRID44_WIDTH * 3 // 2, offset_y=GRID44_HEIGHT // 2)
    draw_centered_text('9', scale=scale, offset_x=-GRID44_WIDTH * 3 // 2, offset_y=GRID44_HEIGHT * 3 // 2)
    draw_centered_text('0', scale=scale, offset_x=-GRID44_WIDTH // 2, offset_y=GRID44_HEIGHT * 3 // 2)
    draw_centered_text('·', scale=scale, offset_x=GRID44_WIDTH // 2, offset_y=GRID44_HEIGHT * 3 // 2)
    draw_centered_text('DEL', scale=scale, offset_x=GRID44_WIDTH * 3 // 2, offset_y=GRID44_HEIGHT * 3 // 2)


def draw_btns_step(scale=1.2):
    draw_centered_text('×', scale=scale, offset_x=-GRID44_WIDTH * 3 // 2, offset_y=-GRID44_HEIGHT * 3 // 2)
    draw_centered_text('✓', scale=scale, offset_x=GRID44_WIDTH * 3 // 2, offset_y=-GRID44_HEIGHT * 3 // 2)

    draw_centered_text(input_ph_str or '<Input>', image.COLOR_WHITE, scale, offset_y=-GRID44_HEIGHT * 3 // 2)

    draw_centered_text('1', scale=scale, offset_x=-GRID44_WIDTH * 3 // 2, offset_y=-GRID44_HEIGHT // 2)
    draw_centered_text('2', scale=scale, offset_x=-GRID44_WIDTH // 2, offset_y=-GRID44_HEIGHT // 2)
    draw_centered_text('3', scale=scale, offset_x=GRID44_WIDTH // 2, offset_y=-GRID44_HEIGHT // 2)
    draw_centered_text('4', scale=scale, offset_x=GRID44_WIDTH * 3 // 2, offset_y=-GRID44_HEIGHT // 2)
    draw_centered_text('5', scale=scale, offset_x=-GRID44_WIDTH * 3 // 2, offset_y=GRID44_HEIGHT // 2)
    draw_centered_text('6', scale=scale, offset_x=-GRID44_WIDTH // 2, offset_y=GRID44_HEIGHT // 2)
    draw_centered_text('7', scale=scale, offset_x=GRID44_WIDTH // 2, offset_y=GRID44_HEIGHT // 2)
    draw_centered_text('8', scale=scale, offset_x=GRID44_WIDTH * 3 // 2, offset_y=GRID44_HEIGHT // 2)
    draw_centered_text('9', scale=scale, offset_x=-GRID44_WIDTH * 3 // 2, offset_y=GRID44_HEIGHT * 3 // 2)
    draw_centered_text('0', scale=scale, offset_x=-GRID44_WIDTH // 2, offset_y=GRID44_HEIGHT * 3 // 2)
    draw_centered_text('·', scale=scale, offset_x=GRID44_WIDTH // 2, offset_y=GRID44_HEIGHT * 3 // 2)
    draw_centered_text('DEL', scale=scale, offset_x=GRID44_WIDTH * 3 // 2, offset_y=GRID44_HEIGHT * 3 // 2)


def is_in_btn(x, y, btn_pos):
    return x >= btn_pos[0] and x <= btn_pos[0] + btn_pos[2] and y >= btn_pos[1] and y <= btn_pos[1] + btn_pos[3]


def on_clicked_init(x, y):
    global curr_state

    screen.clear()
    draw_btns_home()
    curr_state = State.HOME


def on_clicked_home(x, y):
    global curr_state, prev_state

    if is_in_btn(x, y, btn_lt_pos):
        screen.clear()
        draw_btns_input()
        curr_state = State.INPUT

    elif is_in_btn(x, y, btn_rt_pos):
        screen.clear()
        # todo
        curr_state = State.STEP

    elif is_in_btn(x, y, btn_lb_pos):
        screen.clear()
        draw_centered_text('Made by Liu Kuan', image.COLOR_PURPLE, offset_y=-20)
        draw_centered_text('https://github.com/chillcicada', image.COLOR_GRAY, 0.8, offset_y=20)
        prev_state = curr_state
        curr_state = State.MESSAGE

    elif is_in_btn(x, y, btn_rb_pos):
        app.set_exit_flag(True)


def on_clicked_input(x, y):
    global curr_state, input_ph_str

    if is_in_btn(x, y, btn_00_pos):
        screen.clear()
        draw_btns_home()
        input_ph_str = ''
        curr_state = State.HOME
        return

    elif is_in_btn(x, y, btn_30_pos):
        pass

    elif is_in_btn(x, y, btn_01_pos):
        input_ph_str += '1'
    elif is_in_btn(x, y, btn_11_pos):
        input_ph_str += '2'
    elif is_in_btn(x, y, btn_21_pos):
        input_ph_str += '3'
    elif is_in_btn(x, y, btn_31_pos):
        input_ph_str += '4'
    elif is_in_btn(x, y, btn_02_pos):
        input_ph_str += '5'
    elif is_in_btn(x, y, btn_12_pos):
        input_ph_str += '6'
    elif is_in_btn(x, y, btn_22_pos):
        input_ph_str += '7'
    elif is_in_btn(x, y, btn_32_pos):
        input_ph_str += '8'
    elif is_in_btn(x, y, btn_03_pos):
        input_ph_str += '9'
    elif is_in_btn(x, y, btn_13_pos):
        input_ph_str += '0'
    elif is_in_btn(x, y, btn_23_pos):
        input_ph_str += '.'
    elif is_in_btn(x, y, btn_33_pos):
        if len(input_ph_str) > 0:
            input_ph_str = input_ph_str[:-1]

    if len(input_ph_str) <= 4:
        screen.draw_rect(0, 0, MAIX_CAM_WIDTH, MAIX_CAM_HEIGHT * 3 // 4, image.COLOR_BLACK, -1)
        draw_btns_input()
    else:
        pass


def on_clicked_message(x, y):
    global curr_state, prev_state

    screen.clear()
    match prev_state:
        case _:
            draw_btns_home()

    curr_state = prev_state


# draw text at center
def draw_centered_text(
    text: str,
    color=image.COLOR_GRAY,
    scale: int | float = 1,
    offset_x=0,
    offset_y=0,
    box_color=image.COLOR_GRAY,
    box_thickness: int = 0,
    outset_x=16,
    outset_y=12,
    x=MAIX_CAM_WIDTH,
    y=MAIX_CAM_HEIGHT,
):
    size = image.string_size(text, scale=scale)
    pos_x = (x - size.width()) // 2 + offset_x
    pos_y = (y - size.height()) // 2 + offset_y
    if box_thickness != 0:
        draw_centered_rect(
            size.width() + 2 * outset_x,
            size.height() + 2 * outset_y,
            box_color,
            box_thickness,
            offset_x,
            offset_y,
            x,
            y,
        )
    screen.draw_string(pos_x, pos_y, text, color, scale=scale)


def draw_centered_rect(
    w: int,
    h: int,
    color=image.COLOR_GRAY,
    thickness: int = -1,  # -1 means fill
    offset_x=0,
    offset_y=0,
    x=MAIX_CAM_WIDTH,
    y=MAIX_CAM_HEIGHT,
):
    pos_x = (x - w) // 2 + offset_x
    pos_y = (y - h) // 2 + offset_y
    screen.draw_rect(pos_x, pos_y, w, h, color, thickness)


def send_message(text: str, style: str = 'INFO', color=image.COLOR_BLACK, scale: int | float = 1):
    global prev_state, curr_state

    prev_state = curr_state
    curr_state = State.MESSAGE

    color_map = {'INFO': image.COLOR_BLUE, 'WARNING': image.COLOR_YELLOW, 'ERROR': image.COLOR_RED}
    box_color = color_map.get(style.upper(), image.COLOR_GRAY)

    screen.clear()
    screen.draw_rect(*btn_msg_pos, box_color, -1)
    draw_centered_text(text, color, scale)


# def init_dobot():
#     try:
#         dobot.connect()
#         time.sleep(1)

#         dobot.ClearError()
#         dobot.EnableRobot(0.2, 0, 0, 0, 1)
#         time.sleep(1)

#         dobot.SpeedFactor(40)
#         dobot.Grab(False)
#     except Exception as _:
#         pass


if __name__ == '__main__':
    draw_centered_text('Touch to start!', scale=1.5)

    while not app.need_exit():
        x, y, pressed = touch.read()

        if pressed and not last_pressed:
            last_pressed = pressed
            match curr_state:
                case State.INIT:
                    on_clicked_init(x, y)
                case State.HOME:
                    on_clicked_home(x, y)
                case State.INPUT:
                    on_clicked_input(x, y)
                case State.MESSAGE:
                    on_clicked_message(x, y)

        elif not pressed:
            last_pressed = pressed

        disp.show(screen)
