from maix import app, display, image, touchscreen

disp = display.Display()
touch = touchscreen.TouchScreen()

MAIX_CAM_WIDTH = disp.width()
MAIX_CAM_HEIGHT = disp.height()

screen = image.Image(MAIX_CAM_WIDTH, MAIX_CAM_HEIGHT)

# run `scp /path/to/MapleMono-Regular.ttf root@10.177.150.1:~/fonts` to upload font file
image.load_font('Maple Mono', '/root/fonts/MapleMono-Regular.ttf', 40)
image.set_default_font('Maple Mono')

current_state = 'INIT'

# +-------------+
# | btn1 | btn2 |
# +-------------+
# | btn3 | btn4 |
# +-------------+

btn1_label = 'RUN'
btn2_label = 'STEP'
btn3_label = 'MORE'
btn4_label = 'EXIT'

btn1_pos = [0, 0, MAIX_CAM_WIDTH // 2, MAIX_CAM_HEIGHT // 2]
btn2_pos = [MAIX_CAM_WIDTH // 2, 0, MAIX_CAM_WIDTH // 2, MAIX_CAM_HEIGHT // 2]
btn3_pos = [0, MAIX_CAM_HEIGHT // 2, MAIX_CAM_WIDTH // 2, MAIX_CAM_HEIGHT // 2]
btn4_pos = [MAIX_CAM_WIDTH // 2, MAIX_CAM_HEIGHT // 2, MAIX_CAM_WIDTH // 2, MAIX_CAM_HEIGHT // 2]


def init_btns():
    draw_centered_text(
        btn1_label,
        scale=2,
        offset_x=-MAIX_CAM_WIDTH // 4,
        offset_y=-MAIX_CAM_HEIGHT // 4,
    )

    draw_centered_text(
        btn2_label,
        scale=2,
        offset_x=MAIX_CAM_WIDTH // 4,
        offset_y=-MAIX_CAM_HEIGHT // 4,
    )

    draw_centered_text(
        btn3_label,
        scale=2,
        offset_x=-MAIX_CAM_WIDTH // 4,
        offset_y=MAIX_CAM_HEIGHT // 4,
    )

    draw_centered_text(
        btn4_label,
        scale=2,
        offset_x=MAIX_CAM_WIDTH // 4,
        offset_y=MAIX_CAM_HEIGHT // 4,
    )


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


def is_in_btn(x, y, btn_pos):
    return x >= btn_pos[0] and x <= btn_pos[0] + btn_pos[2] and y >= btn_pos[1] and y <= btn_pos[1] + btn_pos[3]


def on_clicked(x, y):
    if is_in_btn(x, y, btn1_pos):
        pass

    elif is_in_btn(x, y, btn2_pos):
        pass

    elif is_in_btn(x, y, btn3_pos):
        pass

    elif is_in_btn(x, y, btn4_pos):
        if btn4_label == 'EXIT':
            app.set_exit_flag(True)


if __name__ == '__main__':
    draw_centered_text('Touch to start!', scale=1.5)

    last_x = 0
    last_y = 0
    last_pressed = 0
    in_pressed = 0

    # count = 0

    while not app.need_exit():
        x, y, pressed = touch.read()

        if pressed != last_pressed:
            screen.clear()

            match current_state:
                case 'INIT':
                    init_btns()
                case _:
                    pass

            # screen.clear()
            # draw_centered_text('pH: 7.81', scale=3, color=image.COLOR_BLACK, box_thickness=-1, offset_y=-100)
            # draw_centered_text('pH: 5.81', scale=3, offset_y=100)
            # count += 1

            last_x = x
            last_y = y
            last_pressed = pressed

        if pressed:
            in_pressed = 1
        elif in_pressed:
                print(f'clicked at: ({x}, {y})')
                on_clicked(x, y)
                in_pressed = 0

        # if count == 20:
        #     app.set_exit_flag(True)

        disp.show(screen)
