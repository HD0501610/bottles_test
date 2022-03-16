# @TIME ：2021/1/19
import cv2
import numpy as np
from imutils.perspective import four_point_transform
import imutils


def cv_show(name, img):
    cv2.imshow(name, img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


# 透视变换
def Get_Outline(input_dir):
    image = cv2.imread("bottles/bottle_crate_05.png")   #读图
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)       #原图转灰度图
    blurred = cv2.GaussianBlur(gray, (5,5),0)            #高斯模糊
    edged = cv2.Canny(blurred,75,200)                    #canny边缘检测
    return image,gray,blurred,edged
#找透视变换的轮廓
def Get_cnt(edged):
    cnts = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
    cnts = cnts[1] if  imutils.is_cv2()  else   cnts[0]
    docCnt =None

    if len(cnts) > 0:
        cnts =sorted(cnts,key=cv2.contourArea,reverse=True)
        for c in cnts:
            peri = cv2.arcLength(c,True)                   # 轮廓按大小降序排序
            approx = cv2.approxPolyDP(c,0.02 * peri,True)  # 获取近似的轮廓
            if len(approx) ==4:                            # 近似轮廓有四个顶点
                docCnt = approx
                break
    return docCnt
if __name__=="__main__":
    input_dir = "bottles/bottle_crate_05.png"
    image,gray,blurred,edged = Get_Outline(input_dir)
    docCnt = Get_cnt(edged)
    result_img = four_point_transform(image , docCnt.reshape(4,2))   # 对原始图像进行四点透视变换

# cv_show('image', image)
#cv_show('gray', gray)
#cv_show('blurred', blurred)
#cv_show('edged', edged)
# cv_show('result_img', result_img)

#裁剪
Cropped = result_img[10:375,25:560]
#print(Cropped.shape)
#cv_show('Cropped', Cropped)

Cropped_gray = cv2.cvtColor(Cropped, cv2.COLOR_BGR2GRAY)   #转灰度图
#直方图均衡化
#equ=cv2.equalizeHist(Cropped_gray)
#cv_show('equ', equ)
#自适应均衡化
clahe = cv2.createCLAHE(clipLimit=2.0,tileGridSize=(8,8))
cll = clahe.apply(Cropped_gray)
# cv_show('cll', cll)
#二值化处理
rst,th = cv2.threshold(cll, 120, 255, cv2.THRESH_BINARY)
# cv_show('th', th)

#腐蚀
kernel=np.ones((8,8),np.uint8)
imgEroded=cv2.erode(th,kernel,iterations=1)
# cv_show('imgEroded', imgEroded)

#膨胀
imgDialation=cv2.dilate(imgEroded,kernel,iterations=1)
# cv_show('imgDialation', imgDialation)

#找目标轮廓
(cnts,_) = cv2.findContours(imgDialation, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
#画轮廓
list=[]
imgDialation_RGB=cv2.cvtColor(imgDialation, cv2.COLOR_GRAY2BGR)
for cnt in cnts:
  (x, y, w, h) = cv2.boundingRect(cnt)
  print(x, y, w, h)
  if w > 35:
      cv2.drawContours(imgDialation_RGB,cnt,-1,(0,0,255),2)
      isNG = True
      list.append(cnt)
a=len(list)  #目标数量
print(a)


#如果目标数量大于零（即有故障）
if a>0:
    # cv_show('imgDialation_RGB', imgDialation_RGB)
    print("NOT GOOD")
    #Cropped_RGB = cv2.cvtColor(Cropped, cv2.COLOR_GRAY2BGR)
    # 画目标轮廓的最小外接矩形
    for cnt in list:
        rect = cv2.minAreaRect(cnt)
        box = np.int0(cv2.boxPoints(rect))
        img = cv2.drawContours(Cropped, [box], -1, (0, 255, 0), 3)
    cv2.putText(img, "Not Good", (40, 40), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 255), 3)
    cv_show("Img", img)
    #cv2.imwrite("contoursImage2.jpg", image)
else:           #无故障
    cv2.putText(image, "Good", (50, 50), cv2.FONT_HERSHEY_COMPLEX, 2, (0, 150, 0), 5)
    cv_show("image", image)
    print("GOOD")   #无故障

cv2.imwrite('bottle/crate_05.png', s_bottle)