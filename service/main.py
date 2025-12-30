from maix import app, display, image, time, touchscreen

disp = display.Display()
touch = touchscreen.TouchScreen()

MAIX_CAM_WIDTH = disp.width()
MAIX_CAM_HEIGHT = disp.height()

GRID_WIDTH = MAIX_CAM_WIDTH // 4
GRID_HEIGHT = MAIX_CAM_HEIGHT // 4

screen = image.Image(MAIX_CAM_WIDTH, MAIX_CAM_HEIGHT)

# run `scp /path/to/MapleMono-Regular.ttf root@10.177.150.1:~/fonts` to upload font file
image.load_font('Maple Mono', '/root/fonts/MapleMono-Regular.ttf', 40)
image.set_default_font('Maple Mono')

input_ph_str = ''
current_state = 'INITING'

last_x = 0
last_y = 0
last_pressed = 0

# +-------------+
# | btn1 | btn2 |
# +-------------+
# | btn3 | btn4 |
# +-------------+

btn_lt_label = 'RUN'
btn_rt_label = 'STEP'
btn_lb_label = 'MORE'
btn_rb_label = 'EXIT'

btn_lt_pos = [0, 0, MAIX_CAM_WIDTH // 2, MAIX_CAM_HEIGHT // 2]
btn_rt_pos = [MAIX_CAM_WIDTH // 2, 0, MAIX_CAM_WIDTH // 2, MAIX_CAM_HEIGHT // 2]
btn_lb_pos = [0, MAIX_CAM_HEIGHT // 2, MAIX_CAM_WIDTH // 2, MAIX_CAM_HEIGHT // 2]
btn_rb_pos = [MAIX_CAM_WIDTH // 2, MAIX_CAM_HEIGHT // 2, MAIX_CAM_WIDTH // 2, MAIX_CAM_HEIGHT // 2]

# +---+-------+---+
# | <<|       | OK|
# | 1 | 2 | 3 | 4 |
# | 5 | 6 | 7 | 8 |
# | 9 | 0 | . |DEL|
# +---+-------+---+

btn_back_pos = [0, 0, MAIX_CAM_WIDTH // 4, MAIX_CAM_HEIGHT // 4]
btn_ok_pos = [MAIX_CAM_WIDTH * 3 // 4, 0, MAIX_CAM_WIDTH // 4, MAIX_CAM_HEIGHT // 4]
btn_1_pos = [0, MAIX_CAM_HEIGHT // 4, MAIX_CAM_WIDTH // 4, MAIX_CAM_HEIGHT // 4]
btn_2_pos = [MAIX_CAM_WIDTH // 4, MAIX_CAM_HEIGHT // 4, MAIX_CAM_WIDTH // 4, MAIX_CAM_HEIGHT // 4]
btn_3_pos = [MAIX_CAM_WIDTH // 2, MAIX_CAM_HEIGHT // 4, MAIX_CAM_WIDTH // 4, MAIX_CAM_HEIGHT // 4]
btn_4_pos = [MAIX_CAM_WIDTH * 3 // 4, MAIX_CAM_HEIGHT // 4, MAIX_CAM_WIDTH // 4, MAIX_CAM_HEIGHT // 4]
btn_5_pos = [0, MAIX_CAM_HEIGHT // 2, MAIX_CAM_WIDTH // 4, MAIX_CAM_HEIGHT // 4]
btn_6_pos = [MAIX_CAM_WIDTH // 4, MAIX_CAM_HEIGHT // 2, MAIX_CAM_WIDTH // 4, MAIX_CAM_HEIGHT // 4]
btn_7_pos = [MAIX_CAM_WIDTH // 2, MAIX_CAM_HEIGHT // 2, MAIX_CAM_WIDTH // 4, MAIX_CAM_HEIGHT // 4]
btn_8_pos = [MAIX_CAM_WIDTH * 3 // 4, MAIX_CAM_HEIGHT // 2, MAIX_CAM_WIDTH // 4, MAIX_CAM_HEIGHT // 4]
btn_9_pos = [0, MAIX_CAM_HEIGHT * 3 // 4, MAIX_CAM_WIDTH // 4, MAIX_CAM_HEIGHT // 4]
btn_0_pos = [MAIX_CAM_WIDTH // 4, MAIX_CAM_HEIGHT * 3 // 4, MAIX_CAM_WIDTH // 4, MAIX_CAM_HEIGHT // 4]
btn_dot_pos = [MAIX_CAM_WIDTH // 2, MAIX_CAM_HEIGHT * 3 // 4, MAIX_CAM_WIDTH // 4, MAIX_CAM_HEIGHT // 4]
btn_del_pos = [MAIX_CAM_WIDTH * 3 // 4, MAIX_CAM_HEIGHT * 3 // 4, MAIX_CAM_WIDTH // 4, MAIX_CAM_HEIGHT // 4]


def init_btns(scale=2):
    draw_centered_text(btn_lt_label, scale=scale, offset_x=-MAIX_CAM_WIDTH // 4, offset_y=-MAIX_CAM_HEIGHT // 4)
    draw_centered_text(btn_rt_label, scale=scale, offset_x=MAIX_CAM_WIDTH // 4, offset_y=-MAIX_CAM_HEIGHT // 4)
    draw_centered_text(btn_lb_label, scale=scale, offset_x=-MAIX_CAM_WIDTH // 4, offset_y=MAIX_CAM_HEIGHT // 4)
    draw_centered_text(btn_rb_label, scale=scale, offset_x=MAIX_CAM_WIDTH // 4, offset_y=MAIX_CAM_HEIGHT // 4)


def init_input_btns(scale=2):
    draw_centered_text('<<', scale=scale, offset_x=-GRID_WIDTH * 3 // 2, offset_y=-GRID_HEIGHT * 3 // 2)
    draw_centered_text('OK', scale=scale, offset_x=GRID_WIDTH * 3 // 2, offset_y=-GRID_HEIGHT * 3 // 2)

    draw_centered_text(input_ph_str or 'Input..', scale=scale, offset_y=-GRID_HEIGHT * 3 // 2)

    draw_centered_text('1', scale=scale, offset_x=-GRID_WIDTH * 3 // 2, offset_y=-GRID_HEIGHT // 2)
    draw_centered_text('2', scale=scale, offset_x=-GRID_WIDTH // 2, offset_y=-GRID_HEIGHT // 2)
    draw_centered_text('3', scale=scale, offset_x=GRID_WIDTH // 2, offset_y=-GRID_HEIGHT // 2)
    draw_centered_text('4', scale=scale, offset_x=GRID_WIDTH * 3 // 2, offset_y=-GRID_HEIGHT // 2)
    draw_centered_text('5', scale=scale, offset_x=-GRID_WIDTH * 3 // 2, offset_y=GRID_HEIGHT // 2)
    draw_centered_text('6', scale=scale, offset_x=-GRID_WIDTH // 2, offset_y=GRID_HEIGHT // 2)
    draw_centered_text('7', scale=scale, offset_x=GRID_WIDTH // 2, offset_y=GRID_HEIGHT // 2)
    draw_centered_text('8', scale=scale, offset_x=GRID_WIDTH * 3 // 2, offset_y=GRID_HEIGHT // 2)
    draw_centered_text('9', scale=scale, offset_x=-GRID_WIDTH * 3 // 2, offset_y=GRID_HEIGHT * 3 // 2)
    draw_centered_text('0', scale=scale, offset_x=-GRID_WIDTH // 2, offset_y=GRID_HEIGHT * 3 // 2)
    draw_centered_text('·', scale=scale, offset_x=GRID_WIDTH // 2, offset_y=GRID_HEIGHT * 3 // 2)
    draw_centered_text('DEL', scale=scale, offset_x=GRID_WIDTH * 3 // 2, offset_y=GRID_HEIGHT * 3 // 2)


def is_in_btn(x, y, btn_pos):
    return x >= btn_pos[0] and x <= btn_pos[0] + btn_pos[2] and y >= btn_pos[1] and y <= btn_pos[1] + btn_pos[3]


def on_clicked(x, y, scale=2):
    global current_state

    if is_in_btn(x, y, btn_lt_pos):
        screen.draw_rect(*btn_lt_pos, image.COLOR_GRAY, -1)
        draw_centered_text(btn_lt_label, image.COLOR_BLACK, scale, -MAIX_CAM_WIDTH // 4, -MAIX_CAM_HEIGHT // 4)
        time.sleep(0.1)

        if btn_lt_label == 'RUN':
            screen.clear()
            init_input_btns()
            current_state = 'INPUT'

    elif is_in_btn(x, y, btn_rt_pos):
        screen.draw_rect(*btn_rt_pos, image.COLOR_GRAY, -1)
        draw_centered_text(btn_rt_label, image.COLOR_BLACK, scale, MAIX_CAM_WIDTH // 4, -MAIX_CAM_HEIGHT // 4)
        time.sleep(0.1)

        pass

    elif is_in_btn(x, y, btn_lb_pos):
        screen.draw_rect(*btn_lb_pos, image.COLOR_GRAY, -1)
        draw_centered_text(btn_lb_label, image.COLOR_BLACK, scale, -MAIX_CAM_WIDTH // 4, MAIX_CAM_HEIGHT // 4)
        time.sleep(0.1)

        pass

    elif is_in_btn(x, y, btn_rb_pos):
        screen.draw_rect(*btn_rb_pos, image.COLOR_GRAY, -1)
        draw_centered_text(btn_rb_label, image.COLOR_BLACK, scale, MAIX_CAM_WIDTH // 4, MAIX_CAM_HEIGHT // 4)
        time.sleep(0.1)

        if btn_rb_label == 'EXIT':
            app.set_exit_flag(True)


def on_input_clicked(x, y):
    global current_state, input_ph_str

    if is_in_btn(x, y, btn_back_pos):
        screen.draw_rect(*btn_back_pos, image.COLOR_GRAY, -1)
        draw_centered_text('<<', image.COLOR_BLACK, 2, -GRID_WIDTH * 3 // 2, -GRID_HEIGHT * 3 // 2)
        time.sleep(0.1)

        screen.clear()
        init_btns()
        input_ph_str = ''
        current_state = 'INITED'
        return

    elif is_in_btn(x, y, btn_ok_pos):
        screen.draw_rect(*btn_ok_pos, image.COLOR_GRAY, -1)
        draw_centered_text('OK', image.COLOR_BLACK, 2, GRID_WIDTH * 3 // 2, -GRID_HEIGHT * 3 // 2)
        time.sleep(0.1)
        pass

    elif is_in_btn(x, y, btn_1_pos):
        input_ph_str += '1'
        screen.draw_rect(*btn_1_pos, image.COLOR_GRAY, -1)
        draw_centered_text('1', image.COLOR_BLACK, 2, -GRID_WIDTH * 3 // 2, -GRID_HEIGHT // 2)
        time.sleep(0.1)
    elif is_in_btn(x, y, btn_2_pos):
        input_ph_str += '2'
        screen.draw_rect(*btn_2_pos, image.COLOR_GRAY, -1)
        draw_centered_text('2', image.COLOR_BLACK, 2, -GRID_WIDTH // 2, -GRID_HEIGHT // 2)
        time.sleep(0.1)
    elif is_in_btn(x, y, btn_3_pos):
        input_ph_str += '3'
        screen.draw_rect(*btn_3_pos, image.COLOR_GRAY, -1)
        draw_centered_text('3', image.COLOR_BLACK, 2, GRID_WIDTH // 2, -GRID_HEIGHT // 2)
        time.sleep(0.1)
    elif is_in_btn(x, y, btn_4_pos):
        input_ph_str += '4'
        screen.draw_rect(*btn_4_pos, image.COLOR_GRAY, -1)
        draw_centered_text('4', image.COLOR_BLACK, 2, GRID_WIDTH * 3 // 2, -GRID_HEIGHT // 2)
        time.sleep(0.1)
    elif is_in_btn(x, y, btn_5_pos):
        input_ph_str += '5'
        screen.draw_rect(*btn_5_pos, image.COLOR_GRAY, -1)
        draw_centered_text('5', image.COLOR_BLACK, 2, -GRID_WIDTH * 3 // 2, GRID_HEIGHT // 2)
        time.sleep(0.1)
    elif is_in_btn(x, y, btn_6_pos):
        input_ph_str += '6'
        screen.draw_rect(*btn_6_pos, image.COLOR_GRAY, -1)
        draw_centered_text('6', image.COLOR_BLACK, 2, -GRID_WIDTH // 2, GRID_HEIGHT // 2)
        time.sleep(0.1)
    elif is_in_btn(x, y, btn_7_pos):
        input_ph_str += '7'
        screen.draw_rect(*btn_7_pos, image.COLOR_GRAY, -1)
        draw_centered_text('7', image.COLOR_BLACK, 2, GRID_WIDTH // 2, GRID_HEIGHT // 2)
        time.sleep(0.1)
    elif is_in_btn(x, y, btn_8_pos):
        input_ph_str += '8'
        screen.draw_rect(*btn_8_pos, image.COLOR_GRAY, -1)
        draw_centered_text('8', image.COLOR_BLACK, 2, GRID_WIDTH * 3 // 2, GRID_HEIGHT // 2)
        time.sleep(0.1)
    elif is_in_btn(x, y, btn_9_pos):
        input_ph_str += '9'
        screen.draw_rect(*btn_9_pos, image.COLOR_GRAY, -1)
        draw_centered_text('9', image.COLOR_BLACK, 2, -GRID_WIDTH * 3 // 2, GRID_HEIGHT * 3 // 2)
        time.sleep(0.1)
    elif is_in_btn(x, y, btn_0_pos):
        input_ph_str += '0'
        screen.draw_rect(*btn_0_pos, image.COLOR_GRAY, -1)
        draw_centered_text('0', image.COLOR_BLACK, 2, -GRID_WIDTH // 2, GRID_HEIGHT * 3 // 2)
        time.sleep(0.1)
    elif is_in_btn(x, y, btn_dot_pos):
        input_ph_str += '.'
        screen.draw_rect(*btn_dot_pos, image.COLOR_GRAY, -1)
        draw_centered_text('·', image.COLOR_BLACK, 2, GRID_WIDTH // 2, GRID_HEIGHT * 3 // 2)
        time.sleep(0.1)
    elif is_in_btn(x, y, btn_del_pos):
        if len(input_ph_str) > 0:
            input_ph_str = input_ph_str[:-1]
        screen.draw_rect(*btn_del_pos, image.COLOR_GRAY, -1)
        draw_centered_text('DEL', image.COLOR_BLACK, 2, GRID_WIDTH * 3 // 2, GRID_HEIGHT * 3 // 2)
        time.sleep(0.1)

    if len(input_ph_str) <= 4:
        screen.draw_rect(0, 0, MAIX_CAM_WIDTH, MAIX_CAM_HEIGHT * 3 // 4, image.COLOR_BLACK, -1)
        init_input_btns()
    else:
        pass


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


if __name__ == '__main__':
    draw_centered_text('Touch to start!', scale=1.5)

    while not app.need_exit():
        x, y, pressed = touch.read()

        if pressed and not last_pressed:
            last_pressed = pressed
            match current_state:
                case 'INITING':
                    screen.clear()
                    init_btns()
                    current_state = 'INITED'
                    time.sleep(0.5)
                case 'INITED':
                    on_clicked(x, y)
                case 'INPUT':
                    on_input_clicked(x, y)
        elif not pressed:
            last_pressed = pressed

        disp.show(screen)
