# @TIME ：2021/1/19
import cv2
import numpy as np


def cv_show(name, img):
    cv2.imshow(name, img)
    cv2.waitKey()
    cv2.destroyAllWindows()


bottle = cv2.imread("bottles/bottle_mouth_03.png", cv2.IMREAD_GRAYSCALE)
bsp = bottle.shape  # 获取图片尺寸以供使用
psp = (bsp[1], bsp[0])
# print(bsp)
# cv_show('image',bottle)

'''中值滤波'''
median = cv2.medianBlur(bottle, 3)
# cv_show('median',median)
'''hough圆变换'''
cimg = cv2.cvtColor(bottle, cv2.COLOR_GRAY2BGR)  # 转换成彩色图
circles = cv2.HoughCircles(median, cv2.HOUGH_GRADIENT, 1, 100,
            param1=100, param2=60, minRadius=150, maxRadius=160)  # Hough圆检测
circles = np.uint16(np.around(circles))
# print(circles)
for i in circles[0, :]:    # 遍历circles，i为列表，i中包含多个列表，列表为[x,y,r]圆心坐标和半径
    # draw the outer circle
    cv2.circle(cimg, (i[0], i[1]), i[2], (0, 255, 0), 2)
    # draw the center of the circle
    cv2.circle(cimg, (i[0], i[1]), 2, (0, 0, 255), 3)
# cv_show( 'cimg',cimg)
# 参数
center = (circles[0][0][0], circles[0][0][1])
radius = circles[0][0][2]
circles_x1 = center[0]-radius
circles_y1 = center[1]-radius
circles_x2 = center[0]+radius
circles_y2 = center[1]+radius

'''极坐标变换'''
polarImg = cv2.warpPolar(bottle, (300, 900), center, radius,
                         cv2.INTER_LINEAR + cv2.WARP_POLAR_LINEAR)
# cv_show('polarImg',polarImg)

'''反变换'''
b_bottle = cv2.warpPolar(polarImg, psp, center, radius,
                cv2.INTER_LINEAR + cv2.WARP_POLAR_LINEAR + cv2.WARP_INVERSE_MAP)
# cv_show('b_bottle',b_bottle)

'''处理'''
blur = cv2.blur(b_bottle, (5, 5))  # 均值滤波
# cv_show('blur',blur)

ret, thres = cv2.threshold(blur, 130, 255, cv2.THRESH_BINARY)  # 阈值变换
# cv_show('thres',thres)

kernel = np.ones((5, 5), np.uint8)
opening = cv2.morphologyEx(thres, cv2.MORPH_OPEN, kernel)  # 开运算
# cv_show('opening',opening)

kernel = np.ones((3, 3), np.uint8)
dilate = cv2.dilate(opening, kernel, iterations=5)  # 膨胀
# cv_show('dilate',dilate)

'''找缺陷'''
contours, hierarchy = cv2.findContours(dilate, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
s_bottle = cv2.cvtColor(bottle, cv2.COLOR_GRAY2BGR)
counts = []
for cnt in contours:
    (x, y, w, h) = cv2.boundingRect(cnt)
# print(x, y, w, h)
    if x > circles_x1 and x < circles_x2 and y > circles_y1 and y < circles_y2 and (w > 5 or h > 5):
        cv2.drawContours(s_bottle, cnt, -1, (0, 0, 255), 2)
        counts.append(cnt)

# print('counts=',counts)
if counts:
    cv2.putText(s_bottle, "NOT OK", (50, 50), cv2.FONT_HERSHEY_COMPLEX, 2, (0, 0, 255), 5)
else:
    cv2.putText(s_bottle, "OK", (50, 50), cv2.FONT_HERSHEY_COMPLEX, 2, (0, 200, 0), 5)
cv_show('s_bottle', s_bottle)
cv2.imwrite('bottle/mouth_03.png', s_bottle)
