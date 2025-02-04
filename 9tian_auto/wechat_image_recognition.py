import cv2
import numpy as np


# orb=cv2.ORB.create()
#
# wechat_sys=cv2.imread('./wechat_screen/wechat_sys.png')
# sys = cv2.imread('./sys.png')
#
# wechat_sys_gray = cv2.cvtColor(wechat_sys, cv2.COLOR_BGR2GRAY)
# sys_gray = cv2.cvtColor(sys, cv2.COLOR_BGR2GRAY)
#
# if wechat_sys is None or sys is None:
#     raise ValueError('图像加载失败')
#
# print(orb.detectAndCompute(image=wechat_sys_gray,mask=None))
# print(orb.detectAndCompute(image=sys_gray,mask=None))
#======================================================================================
wechat_green_BGR=(108, 215, 29)
wechat_red_BGR=(48,59,255)
def recognition_color(find_image="sys.png",color=wechat_green_BGR,color_smooth=15,mix_area=4,test=False,blur=False):
    """
    返回找到面积最大的颜色的中心(x,y)
    """
    wechat_sys_color_BGR = np.array([[list(color)]], dtype=np.uint8)  # (1,1,3) 形状
    wechat_sys_color_HSV = cv2.cvtColor(wechat_sys_color_BGR, cv2.COLOR_BGR2HSV)
    print(f'原始颜色：{wechat_sys_color_HSV}')
    smooth = color_smooth
    up_HSV = np.clip(wechat_sys_color_HSV + smooth, [0, 0, 0], [179, 255, 255])
    low_HSV = np.clip(wechat_sys_color_HSV - smooth, [0, 0, 0], [179, 255, 255])
    #FIXME HSV空间转换应该重新定义色相纯度明度的SMOOTH关系
    print(f'取值范围：{up_HSV}---{low_HSV}')
    image = cv2.imread(find_image)# 读取图像
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)# 转换到 HSV 颜色空间
    mask = cv2.inRange(hsv, low_HSV, up_HSV)# 颜色过滤，创建掩码
    if blur:
        blurred = cv2.GaussianBlur(mask, (5, 5), 0)  # 进行高斯模糊（减少噪声）
        mask=blurred
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)# 识别颜色区域轮廓
    print(f"len_contours={len(contours)}")

    contours_dict={}
    for cnt in contours:
        if cv2.contourArea(cnt) > mix_area:  # 过滤掉小面积噪点
            x, y, w, h = cv2.boundingRect(cnt) #计算一个轮廓（contour）的最小外接矩形。
            detail = cv2.moments(cnt)
            # 计算质心坐标
            if detail["m00"] != 0:  # 避免除以零的错误
                cx = int(detail["m10"] / detail["m00"])
                cy = int(detail["m01"] / detail["m00"])
                contours_dict[detail['m00']] = cx, cy
            if test:
                cv2.rectangle(image, (x, y), (x + w, y + h), (0, 0, 255), 2)
    if test:
        print('显示结果')
        # 显示结果
        cv2.imshow("Original", image)
        cv2.imshow("Masked & Blurred", mask)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    if len(contours_dict)==0:
        return False
    return contours_dict[max(list(contours_dict.keys()))]

# print(get_wechat_green())
