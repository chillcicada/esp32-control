import math

from maix import camera, display, image, time

k = 21  # k = 真实距离 / z_trans
img = ''
weizhi_az = []
# 摄像头初始化
cam = camera.Camera(640, 480)
disp = display.Display()
# Apriltag码配置
families = image.ApriltagFamilies.TAG36H11


def calculate_distance(x_trans, y_trans, z_trans, k):  # apriltags 计算距离
    return abs(k * math.sqrt(x_trans * x_trans + y_trans * y_trans + z_trans * z_trans))


while 1:
    img = cam.read()
    img_Small = img.resize(320, 240)  # 降低计算量需要对图片进行缩放处理
    apriltags = img_Small.find_apriltags()
    if apriltags != []:
        for a in apriltags:
            # Apriltags码 读取函数
            corners = a.corners()
            for i in range(4):
                img.draw_line(
                    ((corners[i][0]) * 2),
                    ((corners[i][1]) * 2),
                    ((corners[(i + 1) % 4][0]) * 2),
                    ((corners[(i + 1) % 4][1]) * 2),
                    image.COLOR_GREEN,
                    10,
                )
            # 计算x,y,z轴坐标
            x_trans = a.x_translation()
            y_trans = a.y_translation()
            z_trans = a.z_translation()

            # 距离计算
            distance = int(calculate_distance(x_trans, y_trans, z_trans, k) * 100)  # 保留两位小数，并通过乘100去除小数
            # 坐标获取 ， 正负号代表方向  (k为正值的时候，X,Y,Z方向如下时，摄像头坐标系与工具坐标系方向一致)
            x_zh = -k * x_trans
            y_zh = k * y_trans
            z_zh = -k * z_trans
            print(x_zh, y_zh, z_zh)

    img.draw_rect(320, 240, 30, 30, image.COLOR_RED, 5)  # 在中心绘制中心点
    disp.show(img)
    time.sleep_ms(200)
